/* Javascript for SwiftPluginXBlock. */


function SwiftPluginXBlock(runtime, element) {
    const handlerUrl = runtime.handlerUrl(element, 'get_button_handler');
    const handlerUrlDescription = runtime.handlerUrl(element, 'get_problem_description');
    const handlerUrlSolution = runtime.handlerUrl(element, 'get_problem_solution');
    const handlerUrlHasSolution = runtime.handlerUrl(element, 'has_problem_solution');
    const handlerUrlTitle = runtime.handlerUrl(element, 'get_problem_title');
    const handlerUrlLanguage = runtime.handlerUrl(element, 'get_problem_language');
    const showButtonsUrl = runtime.handlerUrl(element, 'show_buttons');

    var myCodeMirror = null;
    var solutionCodeMirror = null;

    const run_btn = document.getElementById('run-btn');
    run_btn.onclick = function (eventObject) {
        var user_code = myCodeMirror.getValue();
        $.ajax({
            type: "POST",
            url: handlerUrl,
            data: JSON.stringify({type: 'run', code: user_code}),
            success: updateResponse,
            error: handleError
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

    const response_title = document.getElementById('response-title')

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

    function init_solution() {
        $.ajax({
            type: "POST",
            url: handlerUrlHasSolution,
            data: JSON.stringify({}),
            success: function (data) {
                console.log('solution')
                console.log(data)
                if (data.has_solution_defined) {
                    solution_btn.hidden = false
                    get_solution()
                } else {
                    solution_btn.hidden = true
                }
            }
        })
    }

    function on_init() {
        init_description();
        init_title();
        init_language();
        init_buttons();
    }

    function init_buttons() {
        $.ajax({
            type: "POST",
            url: showButtonsUrl,
            data: JSON.stringify({}),
            success: function (data) {
                const is_run_hidden = data.show_run_button === false
                const is_submit_hidden = data.show_submit_button === false
                run_btn.hidden = is_run_hidden
                submit_btn.hidden = is_submit_hidden
                response_title.hidden = is_submit_hidden && is_run_hidden
            }
        });
    }

    function init_language() {
        $.ajax({
            type: "POST",
            url: handlerUrlLanguage,
            data: JSON.stringify({}),
            success: function (data) {
                init_code_mirror(data.problem_language)
            }
        });
    }

    function init_code_mirror(mode) {
        const codemirror_config = {
            value: "// Your code here.",
            lineNumbers: true,
            mode: mode,
            lineWrapping: true,
            indentWithTabs: true,
            lineWiseCopyCut: true,
            autoCloseBrackets: true,
        }
        var myTextArea = document.getElementById("code-area");
        myCodeMirror = CodeMirror(function (elt) {
            myTextArea.parentNode.replaceChild(elt, myTextArea);
        }, codemirror_config);
        myCodeMirror.setSize('100%');
        const solutionTextArea = document.getElementById("code-solution-area");
        solutionCodeMirror = CodeMirror(function (elt) {
            solutionTextArea.parentNode.replaceChild(elt, solutionTextArea);
        }, codemirror_config);
        solutionCodeMirror.setSize('100%');
        init_solution()
    }


    function get_solution() {
        $.ajax({
            type: "POST",
            url: handlerUrlSolution,
            data: JSON.stringify({}),
            success: updateProblemSolution
        });
    }


    function setOutput(response) {
        const compilation_response = response.response.output
        let color = response.response.success ? "#33691E" : "#B00020"
        if (response.response.success) {
            document.getElementById('response-txt').innerHTML = compilation_response;
        } else if (response.response.diff) {
            document.getElementById('response-txt').innerHTML = response.response.diff;
        } else {
            document.getElementById('response-txt').innerHTML = compilation_response;
        }

        document.getElementById('response-title').style.color = color;
    }

    function updateResponse(response) {
        if (response.error) {
            setError(response.error)
        } else {
            setOutput(response)
        }
    }

    function setError(error) {
        document.getElementById('response-txt').innerHTML = error;
        document.getElementById('response-title').style.color = "#B00020";
    }

    function handleError(response) {
        const compilation_response = response.response
        const diff_response = response.diff
        const output_response = compilation_response + '</br>' + diff_response
        setError(output_response)
    }

    function updateProblemDescription(response) {
        const myAssigmentTextArea = document.getElementById("assigment-instructions-text");
        const converter = new showdown.Converter();
        const html = converter.makeHtml(response.problem_description);
        myAssigmentTextArea.innerHTML = html;
    }

    function updateProblemTitle(response) {
        const myAssigmentTextArea = document.getElementById("assignment-title");
        const converter = new showdown.Converter();
        const html = converter.makeHtml(response.problem_title);
        myAssigmentTextArea.innerHTML = html;
    }

    function updateProblemSolution(response) {
        solutionCodeMirror.setValue(response.problem_solution)
    }

    $(function ($) {
        /* Here's where you'd do things on page load. */
        on_init()
    });
}

