"""TO-DO: Write a description of what this XBlock is."""

import pkg_resources
from web_fragments.fragment import Fragment
from xblock.core import XBlock
from xblock.fields import String, Scope
from xblockutils.studio_editable import StudioEditableXBlockMixin
import difflib
from io import StringIO
import logging
import requests
import json


def get_server_url(url: str):
    if url.startswith("http"):
        return url
    else:
        return "https://" + url


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
        default="",
        scope=Scope.settings,
        help="Problem id used by the Api to checkcode"
    )

    api_url_submit = String(
        default="",
        scope=Scope.settings,
        help="URL api used to check the code (submit final response)"
    )

    api_url_run = String(
        default="",
        scope=Scope.settings,
        help="URL api used to run the code (run code by api)"
    )

    problem_title = String(
        default="Programming Exercise",
        scope=Scope.settings,
        help="Problem title",
    )

    api_key = String(
        default="password",
        scope=Scope.preferences,
        help="Key to send to API",
    )

    problem_description = String(
        default="Problem description here!",
        scope=Scope.settings,
        help="Problem description in Markdown Language",
        multiline_editor=True
    )

    # problem_solution = String(
    #     default="",
    #     scope=Scope.settings,
    #     help="Problem solution in code",
    #     multiline_editor=True
    # )

    problem_language = String(
        default="text/x-swift",
        scope=Scope.settings,
        help="Example: text/x-kotlin. Supported languages can be found at https://codemirror.net/5/mode/"
    )

    editable_fields = [
        'problem_id',
        'problem_description',
        'problem_title',
        # 'problem_solution',
        'problem_language',
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
        print(self.problem_language)
        html = self.resource_string("static/html/swiftplugin.html")
        frag = Fragment(html.format(self=self))
        frag.add_javascript_url("https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.2/codemirror.js")
        frag.add_javascript_url(self.get_mode_url(self.problem_language))
        frag.add_javascript_url("https://cdnjs.cloudflare.com/ajax/libs/showdown/1.9.1/showdown.min.js")
        frag.add_css(self.resource_string("static/css/swiftplugin.css"))
        frag.add_javascript(self.resource_string("static/js/src/swiftplugin.js"))
        frag.add_css_url("https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css")
        frag.add_css_url("https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.32.0/codemirror.css")
        frag.add_javascript_url("https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/js/bootstrap.min.js")
        frag.add_javascript_url("https://cdnjs.cloudflare.com/ajax/libs/popper.js/2.11.5/umd/popper.min.js")
        frag.add_javascript_url("https://codemirror.net/5/addon/search/search.js")
        frag.add_javascript_url("https://codemirror.net/5/addon/edit/closebrackets.js")
        frag.add_javascript_url("https://codemirror.net/5/addon/search/searchcursor.js")
        frag.add_javascript_url("https://codemirror.net/5/addon/search/jump-to-line.js")
        frag.add_javascript_url("https://codemirror.net/5/addon/dialog/dialog.js")
        frag.add_javascript_url("https://codemirror.net/5/addon/fold/foldcode.js")

        frag.add_css_url("https://codemirror.net/5/addon/dialog/dialog.css")
        frag.add_javascript_url(
            "https://cdnjs.cloudflare.com/ajax/libs/bootstrap/5.0.0-beta2/js/bootstrap.bundle.min.js")
        frag.add_css_url("https://d2l03dhf2zcc6i.cloudfront.net/css/custom.css")
        frag.add_css_url("https://d2l03dhf2zcc6i.cloudfront.net/css/style.css")
        frag.add_css_url(
            "https://fonts.googleapis.com/css2?family=Archivo+Black&family=Roboto:ital,wght@0,400;0,700;1,400;1,700&display=swap")
        frag.initialize_js('SwiftPluginXBlock')
        return frag

    @XBlock.json_handler
    def get_button_handler(self, data, suffix=''):
        """
        An example handler, which increments the data.
        """
        response = {}

        if "code" not in data.keys():
            logging.error("non code data in request!")
            response['status'] = "Empty code!"
            return response

        self.code = data['code']

        response['code'] = self.code
        if "type" not in data.keys():
            logging.error("non request type in request")
            response["status"] = "Non request type"
            return response

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
    def get_problem_title(self, data, suffix=''):
        return {
            'problem_id': self.problem_id,
            'problem_title': self.problem_title
        }

    # @XBlock.json_handler
    # def get_problem_solution(self, data, suffix=''):
    #     return {
    #         'problem_id': self.problem_id,
    #         'problem_solution': self.problem_solution
    #     }

    @XBlock.json_handler
    def get_problem_language(self, data, suffix=''):
        return {
            'problem_id': self.problem_id,
            'problem_language': self.problem_language
        }

    # @XBlock.json_handler
    # def has_problem_solution(self, data, suffix=''):
    #     return {
    #         'problem_id': self.problem_id,
    #         'has_solution_defined': self.problem_solution and self.problem_solution.strip()
    #     }

    @XBlock.json_handler
    def show_buttons(self, data, suffix=''):
        show_run_button = bool(self.api_url_run and self.api_url_run.isspace())
        show_submit_button = bool(self.api_url_submit and self.api_url_submit.isspace())
        return {
            'show_run_button': show_run_button,
            'show_submit_button': show_submit_button,
        }

    def handle_run_request(self):
        r = requests.post(get_server_url(self.api_url_run), json=self.build_request_body())
        return r.json()

    def handle_submit_request(self):
        r = requests.post(get_server_url(self.api_url_submit), json=self.build_request_body())
        return r.json()

    def build_request_body(self):
        body = {
            "code": self.code,
            "language": self.problem_language
        }
        return json.dumps(body)

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

    _modeUrl = {
        "text/x-swift": "https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.2/mode/swift/swift.js",
        "text/x-csrc": "https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.2/mode/clike/clike.js",
        "text/x-c++src": "https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.2/mode/clike/clike.js",
        "text/x-csharp": "https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.2/mode/clike/clike.js",
        "text/x-java": "https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.2/mode/clike/clike.js",
        "text/x-objectivec": "https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.2/mode/clike/clike.js",
        "text/x-scala": "https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.2/mode/clike/scala.js",
        "text/x-squirrel": "https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.2/mode/clike/clike.js",
        "text/apl": "https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.2/mode/apl/apl.js",
        "text/x-ttcn-asn": "https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.2/mode/asn.1/asn.1.js",
        "text/x-python": "https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.2/mode/python/python.js",
        "text/x-kotlin": "https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.2/mode/clike/clike.js",
    }

    def get_mode_url(self, mode):
        normalized_mode = mode.strip().lower()
        return self._modeUrl[normalized_mode]
