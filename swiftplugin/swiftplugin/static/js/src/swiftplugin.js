/* Javascript for SwiftPluginXBlock. */


function SwiftPluginXBlock(runtime, element) {
    const handlerUrl = runtime.handlerUrl(element, 'get_button_handler');
    const handlerProblemUrl = runtime.handlerUrl(element, 'get_problem_info')

    var myCodeMirror = null;
    var solutionCodeMirror = null;

    const run_btn = document.getElementById('run-btn');

    function getCodeAndMode() {
        var user_code = myCodeMirror.getValue()
        var code_mode = myCodeMirror.getMode()
        var mode = code_mode.helperType ? code_mode.helperType : code_mode.name;
        return {user_code, mode};
    }

    run_btn.onclick = function (eventObject) {
        const {user_code, mode} = getCodeAndMode();
        $.ajax({
            type: "POST",
            url: handlerUrl,
            data: JSON.stringify({type: 'run', code: user_code, language: mode}),
            success: updateResponse,
            error: handleError
        });
    }

    const submit_btn = document.getElementById('submit-btn');
    submit_btn.onclick = function (eventObject) {
        const {user_code, mode} = getCodeAndMode();
        $.ajax({
            type: "POST",
            url: handlerUrl,
            data: JSON.stringify({type: 'submit', code: user_code, language: mode}),
            success: updateResponse
        });
    }

    const solution_btn = document.getElementById('btn-solution')

    const response_title = document.getElementById('response-title')

    function init_problem() {
        $.ajax({
            type: "POST",
            url: handlerProblemUrl,
            data: JSON.stringify({}),
            success: updateProblem
        })
    }

    const showdownOptions = {
        tables: true,
        emoji: true,
        tasklists: true,
        strikethrough: true,
        parseImgDimensions: true,
        openLinksInNewWindow: true
    }

    function on_init() {
        init_problem()
    }

    function init_code_mirror(response) {
        const codemirror_config = {
            value: response.starter_code,
            lineNumbers: true,
            mode: response.problem_language,
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
        const solutionmirror_config = codemirror_config
        solutionmirror_config.readOnly = true
        const solutionTextArea = document.getElementById("code-solution-area");
        solutionCodeMirror = CodeMirror(function (elt) {
            solutionTextArea.parentNode.replaceChild(elt, solutionTextArea);
        }, solutionmirror_config);
        solutionCodeMirror.setSize('100%');
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

    function updateValues(response) {
        $(`#select-lang-btn`).text(response.display_language);
        if (!response?.allowed_languages?.length) $(`#select-lang-btn`).addClass("disabled");
        $.each(response.allowed_languages, function (key, value) {
            $(`#ul-1`).append($('<li>', {
                class: "dropdown-item",
                value: value[1],
                text: value[1],
                'data-mark': key,
                'click': function () {
                    $(`#select-lang-btn`).text(value[1])
                    myCodeMirror.setOption("mode", value[2])
                }
            }))
        })
    }

    function updateProblem(response) {
        updateValues(response)
        init_code_mirror(response)
        updateProblemDescription(response)
        updateProblemTitle(response)
        if (response.has_solution_defined) {
            solution_btn.hidden = false
            updateProblemSolution(response)
        } else {
            solution_btn.hidden = true
        }
        const is_run_hidden = response.show_run_button === false
        const is_submit_hidden = response.show_submit_button === false
        run_btn.hidden = is_run_hidden
        submit_btn.hidden = is_submit_hidden
        response_title.hidden = is_submit_hidden && is_run_hidden
    }

    function updateProblemDescription(response) {
        if (!response.problem_description) {
            console.log('No problem description')
            return
        }
        const myAssigmentTextArea = document.getElementById("assigment-instructions-text");
        const converter = new showdown.Converter(showdownOptions);
        let html = converter.makeHtml(response.problem_description);
        const regex = /<table>/g;
        html = html.replace(regex, '<table class="table table-striped table-sm">');
        myAssigmentTextArea.innerHTML = `<div class="class table-responsive">${html}</div>`;
    }

    function updateProblemTitle(response) {
        if (!response.problem_title) {
            console.log('No problem title')
            return
        }
        const myAssigmentTextArea = document.getElementById("assignment-title");
        const converter = new showdown.Converter(showdownOptions);
        const html = converter.makeHtml(response.problem_title);
        myAssigmentTextArea.innerHTML = html;
    }

    function updateProblemSolution(response) {
        if (!response.problem_solution) {
            console.log('No problem solution')
            return
        }
        solutionCodeMirror.setValue(response.problem_solution)
    }

    $(function ($) {
        /* Here's where you'd do things on page load. */
        on_init()
    });
}

