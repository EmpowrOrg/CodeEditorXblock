/* Javascript for SwiftPluginXBlock. */

function SwiftPluginXBlock(runtime, element) {
    function updateResponse(response) {
        document.getElementById('response-txt').innerHTML = response.response;
    }
    function updateProblemDescription(response) {
        var myAssigmentTextArea = document.getElementById("assigment-instructions-text");
        converter = new showdown.Converter();
        html = converter.makeHtml(response.problem_description);
        myAssigmentTextArea.innerHTML = html;
    }
    function updateProblemSolution(response){
        var myTextArea = document.getElementById("code-solution-area");
        myCodeMirror = CodeMirror(function (elt) {
            myTextArea.parentNode.replaceChild(elt, myTextArea);
        }, {
            value: response.problem_solution,
            lineNumbers: true,
            mode: "swift",
            lineWrapping: true,
            readOnly : true,
        });
        myCodeMirror.setSize('100%','100%');
    }
    var handlerUrl = runtime.handlerUrl(element, 'button_handler');
    var handlerUrlDescription = runtime.handlerUrl(element,'get_problem_description');
    var handlerUrlSolution = runtime.handlerUrl(element,'get_problem_solution');
    var handlerUrlHasSolution = runtime.handlerUrl(element,'has_problem_solution');

    var myCodeMirror = null;

    codemirror_config = {
        value: "// Your code here.",
        lineNumbers: true,
        mode: "swift",
        lineWrapping: true
    }

    const run_btn = document.getElementById('run-btn');
    run_btn.onclick = function (eventObject) {
        var user_code = myCodeMirror.getValue();
        $.ajax({
            type: "POST",
            url: handlerUrl,
            data: JSON.stringify({type: 'run', code: user_code}),
            success: updateResponse
        });
    }

    const submit_btn = document.getElementById('submit-btn');
    submit_btn.onclick = function (eventObject) {
        var user_code = myCodeMirror.getValue();
        $.ajax({
            type: "POST",
            url: handlerUrl,
            data: JSON.stringify({type: 'submit', code: user_code}),
            success: updateResponse
        });
    }

    const solution_btn = document.getElementById('btn-solution')

    function init_description(){
        $.ajax({
            type: "POST",
            url: handlerUrlDescription,
            data: JSON.stringify({}),
            success: updateProblemDescription
        });
    }
    
    function on_init(){
        init_description();
        $.ajax({
            type: "POST",
            url: handlerUrlHasSolution,
            data: JSON.stringify({}),
            success: function(data){
                if (data.has_solution_defined){
                    solution_btn.onclick = function (eventObject){
                        init_solution();
                    }
                }else{
                    solution_btn.remove()
                }
            }
        })
    }


    function init_solution(){
        $.ajax({
            type: "POST",
            url: handlerUrlSolution,
            data: JSON.stringify({}),
            success: updateProblemSolution
        });
    }


    $(function ($) {
        /* Here's where you'd do things on page load. */
        var myTextArea = document.getElementById("code-area");
        myCodeMirror = CodeMirror(function (elt) {
            myTextArea.parentNode.replaceChild(elt, myTextArea);
        }, codemirror_config);
        myCodeMirror.setSize('100%','100%');
        on_init()
    });
}

