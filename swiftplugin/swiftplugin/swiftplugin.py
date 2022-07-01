"""TO-DO: Write a description of what this XBlock is."""

import pkg_resources
from web_fragments.fragment import Fragment
from xblock.core import XBlock
from xblock.fields import String, Scope
from xblockutils.studio_editable import StudioEditableXBlockMixin
import difflib, sys
from io import StringIO
import logging
import requests


class SwiftPluginXBlock(
    StudioEditableXBlockMixin,
    XBlock):
    """
    TO-DO: document what your XBlock does.
    """

    code = String(
        default="",
        scope=Scope.user_state,
        help="User code",
    )
    
    problem_id = String(
        default="Example problem id",
        scope=Scope.settings,
        help="Problem id used by the Api to checkcode"
	)
    
    api_url_submit = String(
        default="Example api url",
        scope=Scope.settings,
        help="URL api used to check the code (submit final response)"
	)
    
    api_url_run = String(
        default="Example api url",
        scope=Scope.settings,
        help="URL api used to run the code (run code by api)"
	)

    problem_description = String(
        default="Problem description here!",
        scope=Scope.settings,
        help="Problem description in Markdown Language",
        multiline_editor=True
    )

    problem_solution = String(
        default="print('Hello, World!')",
        scope=Scope.settings,
        help="Problem solution in code",
        multiline_editor=True
    )

    editable_fields = [
        'problem_id',
        'problem_description',
        'problem_solution',
        'api_url_run',
        'api_url_submit'
    ]

    def resource_string(self, path):
        """Handy helper for getting resources from our kit."""
        data = pkg_resources.resource_string(__name__, path)
        return data.decode("utf8")

    @XBlock.supports('multi_device')
    def student_view(self, context=None):
        """
        The primary view of the SwiftPluginXBlock, shown to students
        when viewing courses.
        """

        html = self.resource_string("static/html/swiftplugin.html")
        frag = Fragment(html.format(self=self))
        frag.add_javascript_url("https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.2/codemirror.js")
        frag.add_javascript_url("https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.2/mode/swift/swift.js")
        frag.add_css(self.resource_string("static/css/swiftplugin.css"))
        frag.add_javascript(self.resource_string("static/js/src/swiftplugin.js"))
        frag.add_css_url("https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css")
        frag.add_css_url("https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.32.0/codemirror.css")
        frag.add_javascript_url("https://cdnjs.cloudflare.com/ajax/libs/showdown/1.9.1/showdown.min.js")
        frag.add_javascript_url("https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/js/bootstrap.min.js")
        frag.add_javascript_url("https://cdnjs.cloudflare.com/ajax/libs/popper.js/2.11.5/umd/popper.min.js")
        frag.add_javascript_url("https://codemirror.net/addon/search/search.js")
        frag.add_javascript_url("https://codemirror.net/addon/edit/closebrackets.js")
        frag.add_javascript_url("https://codemirror.net/addon/search/searchcursor.js")
        frag.add_javascript_url("https://codemirror.net/addon/search/jump-to-line.js")
        frag.add_javascript_url("https://codemirror.net/addon/dialog/dialog.js")
        frag.add_javascript_url("https://codemirror.net/addon/fold/foldcode.js")
        frag.add_css_url("https://codemirror.net/addon/dialog/dialog.css")
        frag.add_javascript_url("https://cdnjs.cloudflare.com/ajax/libs/aos/2.3.4/aos.js")
        frag.add_javascript_url("https://d2l03dhf2zcc6i.cloudfront.net/js/theme.js")
        frag.add_javascript_url("https://cdnjs.cloudflare.com/ajax/libs/jquery.countdown/2.2.0/jquery.countdown.min.js")
        frag.add_javascript_url("https://cdnjs.cloudflare.com/ajax/libs/jquery.isotope/3.0.6/isotope.pkgd.min.js")
        frag.add_javascript_url(
            "https://cdnjs.cloudflare.com/ajax/libs/jquery.imagesloaded/4.1.4/imagesloaded.pkgd.min.js")
        frag.add_javascript_url("https://cdnjs.cloudflare.com/ajax/libs/countup.js/2.0.6/countUp.umd.js")
        frag.add_javascript_url("https://cdnjs.cloudflare.com/ajax/libs/mapbox-gl/1.10.1/mapbox-gl.js")
        frag.add_javascript_url("https://cdnjs.cloudflare.com/ajax/libs/masonry/4.2.2/masonry.pkgd.min.js")
        frag.add_javascript_url("https://cdnjs.cloudflare.com/ajax/libs/feather-icons/4.28.0/feather.min.js")
        frag.add_javascript_url("https://cdnjs.cloudflare.com/ajax/libs/Swiper/6.4.9/swiper-bundle.min.js")
        frag.add_javascript_url("https://cdnjs.cloudflare.com/ajax/libs/fancybox/3.5.7/jquery.fancybox.min.js")
        frag.add_javascript_url(
            "https://cdnjs.cloudflare.com/ajax/libs/bootstrap/5.0.0-beta2/js/bootstrap.bundle.min.js")
        frag.add_javascript_url("https://cdnjs.cloudflare.com/ajax/libs/jquery/3.5.1/jquery.min.js")
        frag.add_css_url("https://cdnjs.cloudflare.com/ajax/libs/aos/2.3.4/aos.css")
        frag.add_css_url("https://fonts.googleapis.com/icon?family=Material+Icons")
        frag.add_css_url("https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.1.1/css/all.min.css")
        frag.add_css_url("https://cdnjs.cloudflare.com/ajax/libs/Swiper/8.1.4/swiper-bundle.min.css")
        frag.add_css_url("https://d2l03dhf2zcc6i.cloudfront.net/css/custom.css")
        frag.add_css_url("https://d2l03dhf2zcc6i.cloudfront.net/css/style.css")
        frag.add_css_url(
            "https://fonts.googleapis.com/css2?family=Archivo+Black&family=Roboto:ital,wght@0,400;0,700;1,400;1,700&display=swap")
        frag.initialize_js('SwiftPluginXBlock')

        return frag

    @XBlock.json_handler
    def button_handler(self, data, suffix=''):
        """
        An example handler, which increments the data.
        """
        response = {}

        if "code" not in data.keys():
            logging.error("non code data in request!")
            response['status'] = "Empty code!"

        self.code = data['code']

        response['code'] = self.code
        if "type" not in data.keys():
            logging.error("non request type in request")
            response["status"] = "Non request type"

        if 'run' in data['type']:
            api_respo = self.handle_run_request()
            response['status'] = "Executed code"
            response['response'] = api_respo

        elif 'submit' in data['type']:
            api_respo = self.handle_submit_request()
            response['status'] = "Submitted code"
            response['response'] = api_respo['message']
            response['diff'] = self.calculate_diff(expected_output=api_respo['expected_output'],
                                                   actual_output=api_respo['user_output'])

        else:
            response["status"] = "No valid type request"

        return response

    @XBlock.json_handler
    def get_problem_description(self, data, suffix=''):
        return {
            'problem_id': self.problem_id,
            'problem_description': self.problem_description
        }

    @XBlock.json_handler
    def get_problem_solution(self, data, suffix=''):
        return {
            'problem_id': self.problem_id,
            'problem_solution': self.problem_solution
        }

    @XBlock.json_handler
    def has_problem_solution(self, data, suffix=''):
        return {
            'problem_id': self.problem_id,
            'has_solution_defined': self.problem_solution and self.problem_solution.strip()
        }

    def handle_run_request(self):
        r = requests.post(self.api_url_run,data=self.code)
        return r.json()

    def handle_submit_request(self):
        r = requests.post(self.api_url_submit,data=self.code)
        return r.json()

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

    def calculate_diff(self, expected_output: str, actual_output: str):
        # To redirect std output
        mystdout = StringIO()
        d = difflib.Differ()
        mystdout.writelines(list(d.compare(expected_output.splitlines(keepends=True),
                                           actual_output.splitlines(keepends=True))))
        # Read from mystdout output
        diff = mystdout.getvalue()
        return diff
