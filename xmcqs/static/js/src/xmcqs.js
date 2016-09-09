
function XMCQSXBlock(runtime, element) {
    function displayQuestion(question) {
        // reset the elements
        $('#choices, #hint, #current #question').html('');
        
        if(question == false){
           $('#question_block').html('Questions completed!');
            return
        }

        var choices = question.choices;
        $('#question', element).text(question.question);
        $('#question', element).attr('data-id', question.id);

        for(var i in choices){
            var choiceInput = $('<input>', {type: 'radio', value: choices[i].id, name: 'choice'});
            var labelInput = $('<label>', {text: choices[i].choice});

            var inputDiv = $('<div>').append(choiceInput, labelInput);

            $('#choices').append(inputDiv);
        }

        $('#submit').attr('disabled', true);
        $('input[name=choice]').on('change', function(){
            $('#submit').attr('disabled', false);
        });
    }

    var questionUrl = runtime.handlerUrl(element, 'get_question');
    var checkUrl = runtime.handlerUrl(element, 'check_answer');

    function getQuestion(){
        $.ajax({
            type: "POST",
            data: JSON.stringify({'count': 1}),
            url: questionUrl,
            success: displayQuestion
        });
    }
    
    function checkAnswer() {
        var question_id = $('#question', element).attr('data-id');
        var answer_id = $('input[name="choice"]:checked').val();
        var hintGiven = $('#hint').text() != "";
        
        $.ajax({
            type: "POST",
            data: JSON.stringify({'q': question_id, 'ans': answer_id, 'hint_given': hintGiven}),
            url: checkUrl,
            success: function(data){
                $('#correct').text(data.correct_total);
                $('#current').text(data.progress);
                
                if(data.correct == true){
                    displayQuestion(data.new_question);
                }else{
                    if($('#hint').text() == "" && data.hint){
                        $('#hint', element).text('Hint: ' + data.hint);
                        $('#hint', element).show('bounce');
                    }else{
                        displayQuestion(data.new_question);
                    }
                }         
            }
        });
    }


    $('#submit').on('click', function(e){
        checkAnswer();
    });
    
    $(function ($) {
        getQuestion();
    });
}
