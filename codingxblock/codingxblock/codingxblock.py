"""
This plugin allows the students to write swift code and submit it as a problem.
The plugin will send the code to an API that will send a correct or failure response.
If correct, the user will see a confirmation message.
If incorrect, the user will see the differences between their answer and the expected answer.
The user may optionally see the solution code as well.

The teacher will be able to upload what the solution code is.
They will also be able to upload the solution answer.
These two are both required.
The teacher will have a toggle on whether they wish to allow the user see the solution code or not.
"""

import pkg_resources
from web_fragments.fragment import Fragment
from xblock.core import XBlock
from xblock.fields import String, Scope


class CodeEditorXBlock(XBlock):
    """
    Students can write and submit code in response to a problem.
    Teachers can upload and allow students to view solution code.
    """

    # Fields are defined on the class.  You can access them in your code as
    # self.<fieldname>.

    # TO-DO: delete count, and define your own fields.
    placeholder_text = String(
        default="", scope=Scope.user_state,
        help="Some text to test as a field",
    )

    def resource_string(self, path):
        """Handy helper for getting resources from our kit."""
        data = pkg_resources.resource_string(__name__, path)
        return data.decode("utf8")

    # TO-DO: change this view to display your data your own way.
    def student_view(self, context=None):
        """
        The primary view of the CodeEditorXBlock, shown to students
        when viewing courses.
        """
        html = self.resource_string("static/html/codingxblock.html")
        frag = Fragment(html.format(self=self))
        frag.add_css(self.resource_string("static/css/codingxblock.css"))
        frag.add_javascript(self.resource_string("static/js/src/codingxblock.js"))
        frag.initialize_js('CodeEditorXBlock')
        return frag

    # TO-DO: change this handler to perform your own actions.  You may need more
    # than one handler, or you may not need any handlers at all.
    @XBlock.json_handler
    def increment_count(self, data, suffix=''):
        """
        An example handler, which increments the data.
        """
        # Just to show data coming in...
        assert data['hello'] == 'world'

        self.count += 1
        return {"count": self.count}

    # TO-DO: change this to create the scenarios you'd like to see in the
    # workbench while developing your XBlock.
    @staticmethod
    def workbench_scenarios():
        """A canned scenario for display in the workbench."""
        return [
            ("CodeEditorXBlock",
             """<codingxblock/>
             """),
            ("Multiple CodeEditorXBlock",
             """<vertical_demo>
                <codingxblock/>
                <codingxblock/>
                <codingxblock/>
                </vertical_demo>
             """),
        ]
