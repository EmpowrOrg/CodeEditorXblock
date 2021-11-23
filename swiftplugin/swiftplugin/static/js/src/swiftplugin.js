/* Javascript for SwiftPluginXBlock. */

function SwiftPluginXBlock(runtime, element) {
	codemirror_config = {
			value:"// Your code here.",
			lineNumbers: true,
  			mode:  "swift",
			lineWrapping: true
		}
    $(function ($) {
        /* Here's where you'd do things on page load. */
		var myTextArea = document.getElementById("code_area");
		var myCodeMirror = CodeMirror(function(elt){
			myTextArea.parentNode.replaceChild(elt, myTextArea);
		},codemirror_config);
    });
}

