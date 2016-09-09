"""Multiple-choice questions XBlock"""

import pkg_resources

from xblock.core import XBlock
from xblock.fields import Scope, String, List, Boolean, Dict, Integer
from xblock.fragment import Fragment

# ToDo: source of questions?
questions = [
    {
        'id': 1, 'question': 'Which of the following languages is more suited to a structured program?',
        'choices': [
            {'id': 1, 'choice': 'PL/1'}, {'id': 2, 'choice': 'FORTRAN'},
            {'id': 3, 'choice': 'BASIC'}, {'id': 4, 'choice': 'PASCAL'},
        ],
        'correct_choice': 4, 'hint': 'Relax & think!'
    },
    {
        'id': 2,
        'question': 'A computer assisted method for the recording and analyzing of existing or hypothetical systems is?',
        'choices': [
            {'id': 1, 'choice': 'Data transmission'}, {'id': 2, 'choice': 'Data flow'},
            {'id': 3, 'choice': 'Data capture'}, {'id': 4, 'choice': 'Data processing'},
        ],
        'correct_choice': 2, 'hint': 'Relax & think!'
    }, {
        'id': 3, 'question': 'The Eiffel Tower is located where in Paris?',
        'choices': [
            {'id': 1, 'choice': 'Bois de Boulogne'}, {'id': 2, 'choice': 'Champ de Mars'},
            {'id': 3, 'choice': 'Jardin des Plantes'}, {'id': 4, 'choice': 'Parc de Belleville'},
        ],
        'correct_choice': 2, 'hint': 'Relax & think!'
    }, {
        'id': 4, 'question': 'Which Apollo mission landed the first humans on the Moon?',
        'choices': [
            {'id': 1, 'choice': 'Apollo 7'}, {'id': 2, 'choice': 'Apollo 9'},
            {'id': 3, 'choice': 'Apollo 11'}, {'id': 4, 'choice': 'Apollo 13'},
        ],
        'correct_choice': 3, 'hint': 'Relax & think!'
    }, {
        'id': 5, 'question': 'Who starred in the 1959 epic film Ben-Hur?',
        'choices': [
            {'id': 1, 'choice': 'Charlton Heston'}, {'id': 2, 'choice': 'Clark Gable'},
            {'id': 3, 'choice': 'Errol Flynn'}, {'id': 4, 'choice': 'Lee Marvin'},
        ],
        'correct_choice': 1, 'hint': 'Relax & think!'
    },
]


class XMCQSXBlock(XBlock):
    """
    Provides multiple-choice questions block
    """
    question = Dict(default='', scope=Scope.content, help='Question presented to user')
    no_of_correct_answers = Integer(default=0, scope=Scope.user_state, help='No. of correct answers')
    total_questions = Integer(default=5, scope=Scope.content, help='Total questions presented')
    progress = Integer(default=0, scope=Scope.user_state, help='Index of current question being attempted')
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
        html = self.resource_string("static/html/xmcqs.html")
        frag = Fragment(html.format(self=self))
        frag.add_css(self.resource_string("static/css/xmcqs.css"))
        frag.add_javascript(self.resource_string("static/js/src/xmcqs.js"))
        frag.initialize_js('XMCQSXBlock')

        return frag

    def get_new_question(self):
        next_index = self.progress if self.progress == 0 else self.progress + 1
        self.progress += 1

        try:
            question = questions[next_index].copy()
        except IndexError:
            self.completed = True
            return False
        else:
            # only send public data
            question.pop('correct_choice')
            question.pop('hint')

            return question

    @XBlock.json_handler
    def get_question(self, data, suffix=''):
        """
        handler to present question
        """
        return self.get_new_question()

    @XBlock.json_handler
    def check_answer(self, data, suffix=''):
        response = dict(correct=False)

        ans = int(data.get('ans', 0))
        q = int(data.get('q', 0))
        hint_given = data.get('hint_given')

        question = (item for item in questions if item["id"] == q).next()

        if ans == question.get('correct_choice'):
            self.no_of_correct_answers += 1
            response['new_question'] = self.get_new_question()
            response['correct'] = True
        else:
            if hint_given:
                response['new_question'] = self.get_new_question()
            else:
                response['hint'] = question.get('hint')

        response['correct_total'] = self.no_of_correct_answers
        response['progress'] = self.progress

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
