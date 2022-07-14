/* Javascript for SwiftPluginXBlock. */


function SwiftPluginXBlock(runtime, element) {
    function updateResponse(response) {
        const compilation_response = response.response
        const diff_response = response.diff
        const output_response = compilation_response + '</br>' + diff_response
        document.getElementById('response-txt').innerHTML = output_response;
    }
    function updateProblemDescription(response) {
        const myAssigmentTextArea = document.getElementById("assigment-instructions-text");
        const converter = new showdown.Converter();
        const html = converter.makeHtml(response.problem_description);
        myAssigmentTextArea.innerHTML = html;
    }

    function updateProblemTitle(response) {
        const myAssigmentTextArea = document.getElementById("assigment-title");
        const converter = new showdown.Converter();
        const html = converter.makeHtml(response.problem_title);
        myAssigmentTextArea.innerHTML = html;
    }

    function updateProblemSolution(response) {
        const myTextArea = document.getElementById("code-solution-area");
        myCodeMirror = CodeMirror(function (elt) {
            myTextArea.parentNode.replaceChild(elt, myTextArea);
        }, {
            value: response.problem_solution,
            lineNumbers: true,
            mode: "swift",
            lineWrapping: true,
            readOnly: true,
        });
        myCodeMirror.setSize('100%');
    }
    const handlerUrl = runtime.handlerUrl(element, 'button_handler');
    const handlerUrlDescription = runtime.handlerUrl(element, 'get_problem_description');
    const handlerUrlSolution = runtime.handlerUrl(element, 'get_problem_solution');
    const handlerUrlHasSolution = runtime.handlerUrl(element, 'has_problem_solution');
    const handlerUrlTitle = runtime.handlerUrl(element, 'get_problem_title');

    var myCodeMirror = null;

    const codemirror_config = {
        value: "// Your code here.",
        lineNumbers: true,
        mode: "swift",
        lineWrapping: true,
        indentWithTabs: true,
        lineWiseCopyCut: true,
        autoCloseBrackets: true,

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

    function init_description() {
        $.ajax({
            type: "POST",
            url: handlerUrlDescription,
            data: JSON.stringify({}),
            success: updateProblemDescription
        });
    }

    function init_title() {
        $.ajax({
            type: "POST",
            url: handlerUrlTitle,
            data: JSON.stringify({}),
            success: updateProblemTitle
        });
    }

    function on_init() {
        init_description();
        init_title();

        $.ajax({
            type: "POST",
            url: handlerUrlHasSolution,
            data: JSON.stringify({}),
            success: function (data) {
                if (data.has_solution_defined) {
                    solution_btn.onclick = function (eventObject) {
                        init_solution();
                    }
                } else {
                    solution_btn.remove()
                }
            }
        })
    }


    function init_solution() {
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
        myCodeMirror.setSize('100%');
        on_init()
    });
}

