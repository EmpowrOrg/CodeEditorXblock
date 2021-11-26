/* Javascript for SwiftPluginXBlock. */

function SwiftPluginXBlock(runtime, element) {
	function updateResponse(response) {
		document.getElementById('response_txt').innerHTML = response.response;
	}

	var handlerUrl = runtime.handlerUrl(element, 'button_handler');

	var myCodeMirror = null;

	codemirror_config = {
			value:"// Your code here.",
			lineNumbers: true,
  			mode:  "swift",
			lineWrapping: true
		}

	var run_btn = document.getElementById('run_btn');

	run_btn.onclick = function(eventObject){
		var user_code = myCodeMirror.getValue();
		$.ajax({
			type: "POST",
		    url: handlerUrl,
		    data: JSON.stringify({type: 'run',code: user_code}),
		    success: updateResponse
		});
	}

	var submit_btn = document.getElementById('submit_btn');
	submit_btn.onclick = function(eventObject){
		var user_code = myCodeMirror.getValue();
		$.ajax({
			type: "POST",
		    url: handlerUrl,
		    data: JSON.stringify({type: 'submit',code: user_code}),
		    success: updateResponse
		});
	}

    $(function ($) {
        /* Here's where you'd do things on page load. */
		var myTextArea = document.getElementById("code_area");
		myCodeMirror = CodeMirror(function(elt){
			myTextArea.parentNode.replaceChild(elt, myTextArea);
		},codemirror_config);
    });
}

