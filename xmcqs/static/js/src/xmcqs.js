
function XMCQSXBlock(runtime, element) {
    function displayQuestion(question) {
        // reset the elements
        $('#choices, #hint, #current #question').html('');
        
        // if questions completed, display result
        if(!question.question){
           $('#question_block').html('<p>You have completed this quiz. Following is your result.</p>' +
               '<p>Total:' + question.total + '</p><p>Correct: ' + question.correct + '</p>');
            return;
        }

        var choices = question.choices;
        $('#question', element).text(question.question);
        $('#question', element).attr('data-id', question.id);

        for(var i in choices){
            var choiceInput = $('<input>', {type: 'radio', value: parseInt(i) + 1, name: 'choice'});
            var label = $('<label>').append(choiceInput).append(choices[i]);

            var inputDiv = $('<div>').append(label);

            $('#choices').append(inputDiv);
        }

        $('#submit').attr('disabled', true);
    }
    
    var checkUrl = runtime.handlerUrl(element, 'check_answer');
    
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
                        $('#hint', element).show('slow');
                    }else{
                        displayQuestion(data.new_question);
                    }
                }         
            }
        });
    }

    // enable submit only after any selection
    $('#submit').attr('disabled', true);

    $(document).on('change', 'input[name=choice]', function(){
        $('#submit').attr('disabled', false);
    });

    $('#submit').on('click', function(e){
        checkAnswer();
    });
}
