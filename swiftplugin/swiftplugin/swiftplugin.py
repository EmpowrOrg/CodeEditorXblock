"""TO-DO: Write a description of what this XBlock is."""

import pkg_resources
from web_fragments.fragment import Fragment
from xblock.core import XBlock
from xblock.fields import String, Scope, Boolean
from xblockutils.studio_editable import StudioEditableXBlockMixin
import requests
import json


def get_server_url(url: str):
    if url.startswith("http"):
        return url
    else:
        return "https://" + url


@XBlock.wants('user')
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

    starter_code = String(
        default="",
        scope=Scope.settings,
        help="Starter code for user"
    )

    reference_id = String(
        default="",
        scope=Scope.settings,
        help="Problem id used by the Api to check the code"
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
        default="",
        scope=Scope.preferences,
        help="Key to send to API",
    )

    problem_description = String(
        default="",
        scope=Scope.settings,
        help="Problem description in Markdown Language",
        multiline_editor=True
    )

    allow_any_language = Boolean(
        default=False,
        scope=Scope.settings,
        help="Allow users to complete the problem with any supported language",
    )

    has_score = True
    attempt = 1

    problem_solution = String(
        default="",
        scope=Scope.settings,
        help="Problem solution in code",
        multiline_editor=True
    )

    problem_language = String(
        default="text/x-swift",
        scope=Scope.settings,
        help="Example: text/x-kotlin. Supported languages can be found at https://codemirror.net/5/mode/"
    )

    editable_fields = [
        'reference_id',
        'problem_description',
        'problem_title',
        'problem_solution',
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
        html = self.resource_string("static/html/swiftplugin.html")
        frag = Fragment(html.format(self=self))

        frag.add_javascript_url("https://cdnjs.cloudflare.com/ajax/libs/showdown/1.9.1/showdown.min.js")
        frag.add_css(self.resource_string("static/css/swiftplugin.css"))
        frag.add_javascript(self.resource_string("static/js/src/swiftplugin.js"))
        frag.add_css_url("https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css")
        frag.add_javascript_url(
            "https://cdnjs.cloudflare.com/ajax/libs/bootstrap/5.1.3/js/bootstrap.bundle.min.js")
        frag.add_css_url(
            "https://fonts.googleapis.com/css2?family=Archivo+Black&family=Roboto:ital,wght@0,400;0,700;1,400;1,700&display=swap")

        # Code Mirror
        frag.add_javascript_url("https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.2/codemirror.js")
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
        self.initLanguages(frag)
        frag.initialize_js('SwiftPluginXBlock')
        return frag

    def initLanguages(self, frag):
        if self.allow_any_language:
            values = list(self._modeUrl.values())
            for value in values:
                frag.add_javascript_url(value[0])
        else:
            frag.add_javascript_url(self.get_mode_url())

    @XBlock.json_handler
    def get_button_handler(self, data, suffix=''):
        """
        An example handler, which increments the data.
        """
        response = {}

        if "code" not in data.keys():
            response['error'] = "Empty code!"
            return response

        self.code = data['code']
        if "type" not in data.keys():
            response["error"] = "Invalid request type"
            return response

        if "language" not in data.keys():
            response["error"] = "No language specified"
            return response

        language = data["language"]

        if 'run' in data['type']:
            api_respo = self.handle_request(self.api_url_run, language)
            response['response'] = api_respo
            if 'error' in api_respo:
                response['error'] = api_respo['error']
                return response

        elif 'submit' in data['type']:
            api_respo = self.handle_request(self.api_url_submit, language)
            response['response'] = api_respo
            if 'error' in api_respo:
                response['error'] = api_respo['error']
                return response
            self.attempt = self.attempt + 1
            is_final_attempt = api_respo['finalAttempt']
            success = api_respo['success']
            if success:
                self.runtime.publish(self, "grade",
                                     {'value': 1.0,
                                      'max_value': 1.0})
            elif is_final_attempt:
                self.runtime.publish(self, "grade",
                                     {'value': 0.0,
                                      'max_value': 1.0})


        else:
            response["status"] = "No valid type request"

        return response

    @XBlock.json_handler
    def get_problem_info(self, data, suffix=''):
        show_run_button = bool(self.api_url_run and not self.api_url_run.isspace())
        show_submit_button = bool(self.api_url_submit and not self.api_url_submit.isspace())
        return {
            'reference_id': self.reference_id,
            'problem_description': self.problem_description,
            'problem_title': self.problem_title,
            'problem_language': self.problem_language,
            'has_solution_defined': bool(self.problem_solution.strip()),
            'problem_solution': self.problem_solution,
            'show_run_button': show_run_button,
            'show_submit_button': show_submit_button,
            'display_language': self.get_mode_display_language(),
            'allowed_languages': self.get_allowed_languages(),
            'starter_code': self.starter_code,
        }

    def handle_request(self, url, language):
        try:
            r = requests.post(get_server_url(url), json=self.build_request_body(language), headers=self.build_headers())
            return r.json()
        except requests.exceptions.RequestException as e:
            return json.loads(json.dumps({
                'error': str(e)
            }))

    def build_headers(self):
        headers = {
            'Authorization': 'Bearer {}'.format(self.api_key),
            'Content-Type': "application/json",
            'Accept': 'application/json'
        }
        return headers

    def build_request_body(self, language):
        user_service = self.runtime.service(self, 'user')
        xb_user = user_service.get_current_user()
        email = xb_user.emails[0]
        body = {
            'code': self.code,
            'language': language,
            'attempt': self.attempt,
            'referenceId': self.reference_id,
            'email': email,
        }
        return body

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

    _modeUrl = {
        "text/x-swift": ["https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.2/mode/swift/swift.js", "Swift"],
        "text/x-csrc": ["https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.2/mode/clike/clike.js", "C"],
        "text/x-c++src": ["https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.2/mode/clike/clike.js", "C++"],
        "text/x-csharp": ["https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.2/mode/clike/clike.js", "C#"],
        "text/x-java": ["https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.2/mode/clike/clike.js", "Java"],
        "text/x-objectivec": ["https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.2/mode/clike/clike.js",
                              "Objective-C"],
        "text/x-squirrel": ["https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.2/mode/clike/clike.js", "Squirrel"],
        "text/apl": ["https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.2/mode/apl/apl.js", "APL"],
        "text/x-ttcn-asn": ["https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.2/mode/asn.1/asn.1.js", "ASN"],
        "text/x-python": ["https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.2/mode/python/python.js", "Python"],
        "text/x-kotlin": ["https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.2/mode/clike/clike.js", "Kotlin"],
        "text/javascript": ["https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.2/mode/javascript/javascript.js",
                            "Javascript"],
    }

    def get_mode_url(self):
        normalized_mode = self.problem_language.strip().lower()
        return self._modeUrl[normalized_mode][0]

    def get_mode_display_language(self):
        normalized_mode = self.problem_language.strip().lower()
        return self._modeUrl[normalized_mode][1]

    def get_allowed_languages(self):
        if self.allow_any_language:
            keys = list(self._modeUrl.keys())
            values = []
            for key in keys:
                key_values = self._modeUrl[key]
                key_values.append(key)
                values.append(key_values)
            values.sort(key=self.myFunc)
            return values
        else:
            return []

    def myFunc(self, e):
        return e[1]
