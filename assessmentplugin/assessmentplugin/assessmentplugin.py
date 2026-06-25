"""Assessment XBlock — renders a Coppin assessment as an interactive, student-facing quiz.

The UI is a self-contained React component (``static/js/dist/bundle.js``, built from ``frontend/``)
that is the SAME component the Coppin teacher app uses for its "Live preview", so authors and
students see identical rendering. It deliberately does not use Paragon. The block is interactive
only: every question type is answerable and the student's answers are persisted to user state, but
nothing is auto-graded here.
"""

import json

import pkg_resources
import requests
from web_fragments.fragment import Fragment
from xblock.core import XBlock
from xblock.fields import Dict, Scope, String
from xblockutils.studio_editable import StudioEditableXBlockMixin


# Shown in the workbench (and whenever the block is not yet wired to a Coppin backend) so the
# component renders immediately. Mirrors the Coppin assessment JSON contract.
SAMPLE_ASSESSMENT = {
    "id": "sample",
    "title": "Sample assessment",
    "expectedCompletionTimeInMinutes": 10,
    "problems": [
        {
            "id": "p1", "type": "MultipleChoice", "prompt": "Which keyword declares a constant in Swift?",
            "points": 1,
            "options": [
                {"id": "p1a", "text": "var", "order": 0, "isCorrect": False},
                {"id": "p1b", "text": "let", "order": 1, "isCorrect": True},
                {"id": "p1c", "text": "const", "order": 2, "isCorrect": False},
            ],
        },
        {
            "id": "p2", "type": "TrueFalse", "prompt": "Arrays in Swift are value types.", "points": 1,
            "options": [
                {"id": "p2t", "text": "True", "order": 0, "isCorrect": True},
                {"id": "p2f", "text": "False", "order": 1, "isCorrect": False},
            ],
        },
        {
            "id": "p3", "type": "Checkbox", "prompt": "Select every collection type.", "points": 2,
            "options": [
                {"id": "p3a", "text": "Array", "order": 0, "isCorrect": True},
                {"id": "p3b", "text": "Dictionary", "order": 1, "isCorrect": True},
                {"id": "p3c", "text": "Int", "order": 2, "isCorrect": False},
                {"id": "p3d", "text": "Set", "order": 3, "isCorrect": True},
            ],
        },
        {"id": "p4", "type": "TextInput", "prompt": "What operator forms a closed range?", "points": 1,
         "answer": "..."},
        {"id": "p5", "type": "NumberInput", "prompt": "How many bits is a Swift Int on a 64-bit platform?",
         "points": 1, "answer": "64"},
        {"id": "p6", "type": "ShortAnswer", "prompt": "In one sentence, what is an optional?", "points": 2,
         "answer": "A type that may hold a value or nil."},
        {"id": "p7", "type": "LongAnswer",
         "prompt": "Explain value vs. reference semantics and give an example of each.", "points": 4,
         "answer": "Structs/enums are value types (copied); classes are reference types (shared)."},
    ],
}


@XBlock.wants('user')
class AssessmentXBlock(StudioEditableXBlockMixin, XBlock):
    """An interactive assessment backed by Coppin, rendered with the shared React component."""

    display_name = String(
        default="Assessment",
        scope=Scope.settings,
        help="Name shown in Studio's unit outline.",
    )

    reference_id = String(
        default="",
        scope=Scope.settings,
        help="Coppin assessment (or lesson item) reference id to load.",
    )

    api_url = String(
        default="http://localhost:3000",
        scope=Scope.settings,
        help="Base URL of the Coppin public API.",
    )

    api_key = String(
        default="",
        scope=Scope.settings,
        help="Coppin application API key (sent as a Bearer token).",
    )

    assessment_path = String(
        default="assessment",
        scope=Scope.settings,
        help="Path appended to the API base URL to fetch the assessment.",
    )

    # The student's in-progress answers: { problemId: value | [optionIds] }. Interactive only.
    answers = Dict(default={}, scope=Scope.user_state)

    editable_fields = [
        'display_name',
        'reference_id',
        'api_url',
        'api_key',
        'assessment_path',
    ]

    @staticmethod
    def resource_string(path):
        """Load a packaged resource as text."""
        data = pkg_resources.resource_string(__name__, path)
        return data.decode("utf8")

    @XBlock.supports('multi_device')
    def student_view(self, context=None):
        """The student-facing view: a mount point plus the compiled React bundle."""
        html = self.resource_string("static/html/assessmentplugin.html")
        frag = Fragment(html)
        frag.add_css(self.resource_string("static/css/assessmentplugin.css"))
        frag.add_javascript(self.resource_string("static/js/dist/bundle.js"))
        frag.initialize_js('AssessmentXBlock', json_args={"answers": self.answers or {}})
        return frag

    # Studio preview uses the same view.
    def author_view(self, context=None):
        return self.student_view(context)

    @XBlock.json_handler
    def get_assessment(self, data, suffix=''):
        """Return the assessment to render. Falls back to a sample if the block isn't wired up."""
        if not (self.api_url and self.reference_id and self.api_key):
            return {"assessment": SAMPLE_ASSESSMENT}
        try:
            url = self.build_api_url(self.assessment_path)
            body = {
                "referenceId": self.reference_id,
                "studentId": self.student_id(),
                "blockId": self.xblock_id(),
            }
            r = requests.post(url, json=body, headers=self.build_headers(), timeout=15)
            if not r.ok:
                return {"error": "Couldn't load the assessment ({} {}).".format(r.status_code, r.reason)}
            payload = r.json()
            # Accept either {assessment:{...}} or a bare assessment object.
            assessment = payload.get("assessment", payload) if isinstance(payload, dict) else payload
            return {"assessment": assessment}
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}
        except ValueError:
            return {"error": "The assessment response was not valid JSON."}

    @XBlock.json_handler
    def save_answers(self, data, suffix=''):
        """Persist the student's answers (no grading)."""
        incoming = data.get("answers")
        if not isinstance(incoming, dict):
            return {"error": "Expected an 'answers' object."}
        self.answers = incoming
        return {"result": "success"}

    def build_api_url(self, path):
        url = self.api_url
        if not url.endswith('/'):
            url = url + "/"
        url = url + path
        if url.startswith("http"):
            return url
        return "https://" + url

    def build_headers(self):
        return {
            'Authorization': 'Bearer {}'.format(self.api_key),
            'Content-Type': "application/json",
            'Accept': 'application/json',
        }

    def student_id(self):
        try:
            user_service = self.runtime.service(self, 'user')
            xb_user = user_service.get_current_user()
            student_id = xb_user.opt_attrs.get('edx-platform.username')
            if student_id is None:
                student_id = xb_user.opt_attrs.get('xblock-workbench.username')
            return student_id or ''
        except Exception:  # pragma: no cover - workbench / missing service
            return ''

    def xblock_id(self):
        return str(self.scope_ids.usage_id)

    @staticmethod
    def workbench_scenarios():
        """A canned scenario for the XBlock workbench."""
        return [
            ("AssessmentXBlock",
             """<assessmentplugin/>"""),
        ]
