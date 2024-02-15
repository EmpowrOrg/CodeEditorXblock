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
        default="hello-world",
        scope=Scope.settings,
        help="Problem id used by the Api to check the code"
    )

    api_url = String(
        default="http://localhost:3000/assignment",
        scope=Scope.settings,
        help="URL api used to submit the assignment"
    )

    api_key = String(
        default="MjFmOGY3NTgtNGZiOC00NjJjLWFjMmMtODA2ZmViMDlmOWY0.WEpZUGhRa0JtT3ZzZ2c3bk15UGxvTkpyQmdTb1RhMGI=",
        scope=Scope.settings,
        help="Access Key to send to API",
    )

    has_score = True
    code = ""
    points = 1.0

    editable_fields = [
        'reference_id',
        'api_url',
        'api_key',
    ]

    @staticmethod
    def resource_string(path):
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
        frag.initialize_js('SwiftPluginXBlock')
        return frag

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
            is_final_attempt = assignment_response['finalAttempt']
            success = assignment_response['success']
            grade_points = assignment_response['gradePoints']
            if 'solutionCode' in assignment_response:
                response['problem_solution'] = assignment_response['solutionCode']
            if success:
                self.runtime.publish(self, "grade",
                                     {'value': grade_points,
                                      'max_value': self.points})
            elif is_final_attempt:
                self.runtime.publish(self, "grade",
                                     {'value': 0.0,
                                      'max_value': self.points})

        else:
            response["status"] = "No valid type request"

        return response

    @XBlock.json_handler
    def get_problem_info(self, data, suffix=''):
        response = self.handle_assignment_request()
        if 'error' in response:
            print('error response with problem info')
            print(response)
            response['error'] = response['error']
            return response
        assignment_code = self.get_starter_code(assignment_codes=response['assignmentCodes'])
        solution_code = assignment_code.get('solutionCode')
        starter_code = assignment_code['starterCode']
        user_code = assignment_code.get('userCode')
        self.points = response['points']
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
            'user_code': user_code,
        }

    @staticmethod
    def is_blank(my_string):
        if my_string and my_string.strip():
            # myString is not None AND myString is not empty or blank
            return False
        # myString is None OR myString is empty or blank
        return True

    def handle_assignment_request(self):
        try:
            body = {
                'referenceId': self.reference_id,
                'studentId': self.student_id(),
                'blockId': self.xblock_id(),
            }
            print('body')
            print(body)
            url = self.build_api_url("request")
            r = requests.post(url, json=body,
                              headers=self.build_headers())
            if r.ok:
                return r.json()
            else:
                error = json.loads(json.dumps({
                    'error': 'Uh oh, we encountered an error. Inform your teacher of the following error message: {} {}'.format(
                        r.status_code, r.reason)
                }))
                print('error in handle_assignment_request')
                print(error)
                print(r)
                return error
        except requests.exceptions.RequestException as e:
            error = json.loads(json.dumps({
                'error': str(e)
            }))
            print('error in handle_assignment_request')
            print(error)
            return error

    def build_api_url(self, path):
        url = self.api_url
        if not url.endswith('/'):
            url = url + "/"
        url = url + path
        if url.startswith("http"):
            return url
        else:
            return "https://" + url

    def handle_submit_request(self, language):
        try:
            url = self.build_api_url("submit")
            body = self.build_request_body(language)
            r = requests.post(url, json=body, headers=self.build_headers())
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
            url = self.build_api_url("run")
            r = requests.post(url, json=self.build_request_body(language),
                              headers=self.build_headers())
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

    def build_headers(self):
        headers = {
            'Authorization': 'Bearer {}'.format(self.api_key),
            'Content-Type': "application/json",
            'Accept': 'application/json'
        }
        return headers

    def build_request_body(self, language):
        body = {
            'code': self.code,
            'language': language,
            'referenceId': self.reference_id,
            'studentId': self.student_id(),
            'studentExtras': self.student_extras(),
            'studentEmails': self.student_emails(),
        }
        return body

    def student_id(self):
        user_service = self.runtime.service(self, 'user')
        xb_user = user_service.get_current_user()
        student_id = xb_user.opt_attrs.get('edx-platform.username')
        if student_id is None:
            student_id = xb_user.opt_attrs.get('xblock-workbench.username')
        if student_id is None:
            student_id = ''
        return student_id

    def student_extras(self):
        user_service = self.runtime.service(self, 'user')
        xb_user = user_service.get_current_user()
        if xb_user is None:
            return {}
        if xb_user.opt_attrs is None:
            return {}
        return xb_user.opt_attrs

    def student_emails(self):
        user_service = self.runtime.service(self, 'user')
        xb_user = user_service.get_current_user()
        if xb_user is None:
            return []
        if xb_user.emails is not None:
            return xb_user.emails
        if xb_user.opt_attrs.get('xblock-workbench.emails') is not None:
            return xb_user.opt_attrs.get('xblock-workbench.emails')
        if xb_user.opt_attrs.get('edx-platform.emails') is not None:
            return xb_user.opt_attrs.get('edx-platform.emails')
        return []

    def xblock_id(self):
        usage_id = self.scope_ids.usage_id
        return str(usage_id)

    @staticmethod
    def workbench_scenarios():
        """A canned scenario for display in the workbench."""
        return [
            ("SwiftPluginXBlock",
             """<swiftplugin/>
             """),
        ]

    @staticmethod
    def get_starter_code(assignment_codes):
        for assignment_code in assignment_codes:
            if assignment_code['primary']:
                return assignment_code
        return assignment_codes[0]

    def get_allowed_languages(self, assignment_codes):
        values = []
        for assignment_code in assignment_codes:
            key_values = [assignment_code['url'], assignment_code['mime']]
            values.append(key_values)

        values.sort(key=self.myFunc)
        return values

    def myFunc(self, e):
        return e[1]
