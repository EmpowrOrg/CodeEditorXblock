"""TO-DO: Write a description of what this XBlock is."""

import pkg_resources
from web_fragments.fragment import Fragment
from xblock.core import XBlock
from xblock.fields import String, Scope


class SwiftPluginXBlock(XBlock):
    """
    TO-DO: document what your XBlock does.
    """

    code = String(
        default="",
		scope=Scope.user_state,
        help="User code",
    )
    problem_id = String(
        default="0",
        scope=Scope.content,
        help="Problem id used by the Api to checkcode"
	)
    problem_description = String(
        default= "# Problem description here!",
        scope=Scope.content,
        help="Problem description in Markdown Language"
    )
    
    problem_solution = String(
        default="print('Hello, World!')",
        scope=Scope.content,
        help="Problem solution in code"
    )

    def resource_string(self, path):
        """Handy helper for getting resources from our kit."""
        data = pkg_resources.resource_string(__name__, path)
        return data.decode("utf8")


    def student_view(self, context=None):
        """
        The primary view of the SwiftPluginXBlock, shown to students
        when viewing courses.
        """
        html = self.resource_string("static/html/swiftplugin.html")
        frag = Fragment(html.format(self=self))
        frag.add_css(self.resource_string("static/css/swiftplugin.css"))
        frag.add_javascript(self.resource_string("static/js/src/swiftplugin.js"))
        frag.initialize_js('SwiftPluginXBlock')
        return frag


    @XBlock.json_handler
    def button_handler(self, data, suffix=''):
        """
        An example handler, which increments the data.
        """
        response = {}

        if "code" not in data.keys():
            log.error("non code data in request!")
            response['status'] = "Empty code!"

        self.code = data['code']

        response['code'] = self.code
        if "type" not in data.keys():
            log.error("non request type in request")
            response["status"] = "Non request type"

        if 'run' in  data['type']:
            api_respo = self.handle_run_request()
            response['status'] = "Executed code"
            response['response'] = api_respo

        elif 'submit' in data['type']:
            api_respo = self.handle_submit_request()
            response['status'] = "Submitted code"
            response['response'] = api_respo

        else:
            response["status"] = "No valid type request"

        return response

    @XBlock.json_handler
    def get_problem_description(self,data,suffix=''):
        return {
            'problem_id':self.problem_id,
            'problem_description':self.problem_description
        }
        
    @XBlock.json_handler
    def get_problem_solution(self,data,suffix=''):
        return {
            'problem_id':self.problem_id,
            'problem_solution':self.problem_solution
        }
        
    def handle_run_request(self):
        return "ok"

    def handle_submit_request(self):
        return "Error"

    @staticmethod
    def workbench_scenarios():
        """A canned scenario for display in the workbench."""
        return [
            ("SwiftPluginXBlock",
             """<swiftplugin/>
             """),
            ("Multiple SwiftPluginXBlock",
             """<vertical_demo>
                <swiftplugin/>
                <swiftplugin/>
                <swiftplugin/>
                </vertical_demo>
             """),
        ]
