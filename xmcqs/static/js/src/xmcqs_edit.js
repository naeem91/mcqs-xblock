function XMCQSEdit(runtime, element) {
    
    function addNewQuestion() {
        // generate a random number as question ID
        var id = String(Math.random()).split('.')[1];

        var qDiv = $('<div class="question">').append(
            $('<label>', {text: "Question: "}),
            $('<input>', {type: 'text', class: 'question_text', name: 'question_' + id}),
            $('<input>', {type: 'button', class: 'button del-question', value: 'Delete', 'data-id': id})
        );
        var choiceDiv = $('<div class="choices">');
        var hintDiv = $('<div class="hint">').append(
            $('<input>', {type: 'text', placeholder: 'Hint', class: 'hint-input', name: 'hint_' + id})
        );
        
        for(var i=1; i <= 4; i++){
            $('<div>').append(
                $('<label>', {text: "Choice " + i + ": "}),
                 $('<input>', {type: 'text', class: 'choice-input', name: 'choices_' + id}),
                $('<input>', {type: 'radio', name: 'correct_' + id, 'value': i})
            ).appendTo(choiceDiv);
        }

        $('<div>', {id: 'question_' + id, class: 'question_block'}).append(
            qDiv, choiceDiv, hintDiv
        ).appendTo($('#edit_form'));
    }

    function deleteQuestion() {
        var question_id = $(this).attr('data-id');
        $('#question_' + question_id).remove();
    }

    function submitHandler(e) {
        var data = $('#edit_form').serializeArray();

        var handlerUrl = runtime.handlerUrl(element, 'studio_submit');

        $.ajax({
            type: "POST",
            url: handlerUrl,
            data: JSON.stringify(data),
            success: function(result) {
                alert('Successfully saved!')
            }
        });
    }
    
    $('#edit_submit', element).on('click', submitHandler);
    $('#add_question', element).on('click', addNewQuestion);
    $(element).on('click', '.del-question', deleteQuestion);
}