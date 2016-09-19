"""Multiple-choice questions XBlock"""

from collections import defaultdict

from django.template import Template, Context

import pkg_resources

from xblock.core import XBlock
from xblock.fields import Scope, String, List, Boolean, Dict, Integer
from xblock.fragment import Fragment


class XMCQSXBlock(XBlock):
    """
    Provides multiple-choice questions block
    """
    display_name = String(default='MCQS')
    block_name = String(default='MCQS')

    questions = List(default=[('1', {
        'question': 'Which of the following languages is more suited to a structured program?',
        'choices': ['PL/1', 'FORTRAN', 'BASIC', 'PASCAL'],
        'correct': '4', 'hint': 'Relax & think!'
    })], scope=Scope.content, help='Questions presented to user')
    user_answers = Dict(default={'1': 4}, scope=Scope.user_state, help='User answers against each question')

    current_question = Integer(default=0, scope=Scope.user_state, help='Index of question being attempted by user')
    completed = Boolean(default=False, scope=Scope.user_state, help='User has completed this set')

    def resource_string(self, path):
        """Handy helper for getting resources from our kit."""
        data = pkg_resources.resource_string(__name__, path)
        return data.decode("utf8")

    def student_view(self, context=None):
        """
        The primary view of the XMCQSXBlock, shown to students
        when viewing courses.
        """
        if not context:
            context = {}

        context.update({
            'current': self.current_question + 1, 'total': len(self.questions),
            'completed': self.completed
        })

        if self.completed:
            context.update(self.get_result())
        else:
            context.update({'question': self.get_next_question(index=self.current_question)})

        html = Template(self.resource_string("static/html/xmcqs.html")).render(Context(context))
        frag = Fragment(html)
        frag.add_css(self.resource_string("static/css/xmcqs.css"))
        frag.add_javascript(self.resource_string("static/js/src/xmcqs.js"))
        frag.initialize_js('XMCQSXBlock')

        return frag

    def studio_view(self, context=None):
        if not context:
            context = {}

        context.update({'questions': self.questions})

        html = Template(self.resource_string("static/html/xmcqs_edit.html")).render(Context(context))

        frag = Fragment(html)
        frag.add_css(self.resource_string("static/css/xmcqs_edit.css"))
        frag.add_javascript(self.resource_string("static/js/src/xmcqs_edit.js"))
        frag.initialize_js('XMCQSEdit')

        return frag

    def get_next_question(self, index=None):
        """ Get next question from the questions list """

        next_index = index if index is not None else self.current_question + 1

        try:
            question = self.questions[next_index][1].copy()
            question['id'] = self.questions[next_index][0]
        except IndexError:
            self.completed = True
            return self.get_result()
        else:
            # only send public data
            question.pop('correct')
            question.pop('hint')

            self.current_question = next_index

            return question

    def get_result(self):
        """ calculate user result in quiz """

        answers = {q_id: question.get('correct') for q_id, question in self.questions}

        correct_given = [q for q, ans in self.user_answers.items() if answers[q] == ans]

        return {'total': len(answers), 'correct': len(correct_given)}

    @XBlock.json_handler
    def studio_submit(self, data, suffix=''):
        """ Handle studio data submission """

        questions = defaultdict(dict)

        # data extraction
        for obj in data:
            obj_type, question_id = obj.get('name', '_').split('_')
            obj_value = obj.get('value')

            if obj_type == "choices":
                if not questions[question_id].get(obj_type):
                    questions[question_id][obj_type] = []

                questions[question_id][obj_type].append(obj_value)
            else:
                questions[question_id][obj_type] = obj_value

        self.questions = questions.items()

        return {'success': True, 'errors': []}

    @XBlock.json_handler
    def check_answer(self, data, suffix=''):
        """ Check answer and provide next question or hint """

        response = dict(correct=False)

        ans = data.get('ans', 0)
        q = data.get('q', 0)
        hint_given = data.get('hint_given')

        question = (item[1] for item in self.questions if item[0] == q).next()

        # store user responses
        self.user_answers.update({q: ans})

        if ans == question.get('correct'):
            response['new_question'] = self.get_next_question()
            response['correct'] = True
        else:
            if hint_given:
                response['new_question'] = self.get_next_question()
            else:
                response['hint'] = question.get('hint')

        # progress track
        response.update({'current': self.current_question})

        return response

    @staticmethod
    def workbench_scenarios():
        """A canned scenario for display in the workbench."""
        return [
            ("XMCQSXBlock",
             """<xmcqs/>
             """),
            # ("Multiple XMCQSXBlock",
            #  """<vertical_demo>
            #     <xmcqs/>
            #     <xmcqs/>
            #     <xmcqs/>
            #     </vertical_demo>
            #  """),
        ]
