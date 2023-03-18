"""TO-DO: Write a description of what this XBlock is."""

import pkg_resources
from web_fragments.fragment import Fragment
from xblock.core import XBlock
from xblock.fields import String, Scope
from xblockutils.studio_editable import StudioEditableXBlockMixin
import requests
import json


@XBlock.wants('user')
class SwiftPluginXBlock(
    StudioEditableXBlockMixin,
    XBlock):
    """
    TO-DO: document what your XBlock does.
    """

    reference_id = String(
        default="assignment-2",
        scope=Scope.settings,
        help="Problem id used by the Api to check the code"
    )

    api_url_run = String(
        default="http://0.0.0.0:8080/run",
        scope=Scope.content,
        help="URL api used to run the code (run code by api)"
    )

    api_url_assignment = String(
        default="http://0.0.0.0:3000/assignment",
        scope=Scope.content,
        help="URL api used to submit the assignment"
    )

    api_run_key = String(
        default="password",
        scope=Scope.content,
        help="Key to send to API",
    )
    api_assignment_key = String(
        default="password",
        scope=Scope.content,
        help="Key to send to API",
    )

    has_score = True
    attempt = 1
    code = ""

    editable_fields = [
        'reference_id',
        'api_url_run',
        'api_run_key',
        'api_url_assignment',
        'api_assignment_key',
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

        frag.add_javascript_url("https://cdnjs.cloudflare.com/ajax/libs/showdown/2.1.0/showdown.min.js")
        frag.add_css(self.resource_string("static/css/swiftplugin.css"))
        frag.add_javascript(self.resource_string("static/js/src/swiftplugin.js"))
        frag.add_css(self.resource_string("static/css/bootstrap.min.css"))
        frag.add_javascript_url(
            "https://cdnjs.cloudflare.com/ajax/libs/bootstrap/5.1.3/js/bootstrap.bundle.min.js")
        frag.add_css_url(
            "https://fonts.googleapis.com/css2?family=Archivo+Black&family=Roboto:ital,wght@0,400;0,700;1,400;1,"
            "700&display=swap")

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
        self.init_languages(frag)
        frag.initialize_js('SwiftPluginXBlock')
        return frag

    def init_languages(self, frag):
        values = list(self._modeUrl.values())
        for value in values:
            frag.add_javascript_url(value[0])

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
            run_response = self.handle_run_request(language)
            response['response'] = run_response
            if 'error' in run_response:
                response['error'] = run_response['error']
                return response

        elif 'submit' in data['type']:

            assignment_response = self.handle_submit_request(language=language)
            if 'error' in assignment_response:
                response['error'] = assignment_response['error']
                return response
            response['response'] = assignment_response
            self.attempt = self.attempt + 1
            is_final_attempt = assignment_response['finalAttempt']
            success = assignment_response['success']
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
        response = self.handle_assignment_request()
        if 'error' in response:
            response['error'] = response['error']
            return response
        assignment_code = self.get_starter_code(assignment_codes=response['assignmentCodes'])
        solution_code = assignment_code["solutionCode"]
        starter_code = assignment_code['starterCode']
        if starter_code is None:
            starter_code = ""
        return {
            'reference_id': self.reference_id,
            'problem_description': response['instructions'],
            'problem_title': response['title'],
            'problem_language': assignment_code['mime'],
            'has_solution_defined': not self.is_blank(solution_code),
            'problem_solution': solution_code,
            'show_run_button': True,
            'show_submit_button': True,
            'display_language': assignment_code['displayName'],
            'allowed_languages': self.get_allowed_languages(response['assignmentCodes']),
            'starter_code': starter_code,
        }

    def is_blank(self, my_string):
        if my_string and my_string.strip():
            # myString is not None AND myString is not empty or blank
            return False
        # myString is None OR myString is empty or blank
        return True

    def handle_assignment_request(self):
        try:
            body = {
                'referenceId': self.reference_id,
                'supportedLanguageMimes': list(self._modeUrl.keys())
            }
            url = self.buildApiUrl("request")
            r = requests.post(url, json=body,
                              headers=self.build_headers(False))
            if r.ok:
                return r.json()
            else:
                return json.loads(json.dumps({
                    'error': 'Uh oh, we encountered an error. Inform your teacher of the following error message: {} {}'.format(
                        r.status_code, r.reason)
                }))
        except requests.exceptions.RequestException as e:
            return json.loads(json.dumps({
                'error': str(e)
            }))

    def buildApiUrl(self, path):
        url = self.api_url_assignment
        if not self.api_url_assignment.endswith('/'):
            url = url + "/"
        url = url + path
        return get_normalized_url(url)

    def handle_submit_request(self, language):
        try:
            url = self.buildApiUrl("submit")
            body = self.build_request_body(language)
            r = requests.post(url, json=body, headers=self.build_headers(False))
            if r.ok:
                return r.json()
            else:
                return json.loads(json.dumps({
                    'error': 'Uh oh, we encountered an error. Inform your teacher of the following error message: {} {}'.format(
                        r.status_code, r.reason)
                }))
        except requests.exceptions.RequestException as e:
            return json.loads(json.dumps({
                'error': str(e)
            }))

    def handle_run_request(self, language):
        try:
            r = requests.post(get_normalized_url(self.api_url_run), json=self.build_request_body(language),
                              headers=self.build_headers(True))
            if r.ok:
                return r.json()
            else:
                return json.loads(json.dumps({
                    'error': 'Uh oh, we encountered an error. Inform your teacher of the following error message: {} {}'.format(
                        r.status_code, r.reason)
                }))
        except requests.exceptions.RequestException as e:
            return json.loads(json.dumps({
                'error': str(e)
            }))

    def build_headers(self, run):
        if run:
            api_key = self.api_run_key
        else:
            api_key = self.api_assignment_key
        headers = {
            'Authorization': 'Bearer {}'.format(api_key),
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

    def get_starter_code(self, assignment_codes):
        for assignment_code in assignment_codes:
            if assignment_code['primary']:
                return assignment_code
        return assignment_codes[0]

    def get_allowed_languages(self, assignment_codes):
        keys = list(self._modeUrl.keys())
        values = []
        for assignment_code in assignment_codes:
            if assignment_code['mime'] in keys:
                key_values = self._modeUrl[assignment_code['mime']]
                key_values.append(assignment_code['mime'])
                values.append(key_values)

        values.sort(key=self.myFunc)
        return values

    def myFunc(self, e):
        return e[1]
