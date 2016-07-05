"""TO-DO: Write a description of what this XBlock is."""

import pkg_resources

from xblock.core import XBlock
from xblock.fields import Scope, Integer
from xblock.fragment import Fragment


class TimelineXBlock(XBlock):
    """
    This XBlock shows pretty jQuery powered timeline HTML page.
    It currently has no input except edit display_name in edX studio
    but future plans include a form where content author would be able
    to create their own timeline.
    """

    # Fields are defined on the class.  You can access them in your code as
    # self.<fieldname>.

    # TO-DO: delete count, and define your own fields.
    count = Integer(
        default=0, scope=Scope.user_state,
        help="A simple counter, to show something happening",
    )

    def resource_string(self, path):
        """Handy helper for getting resources from our kit."""
        data = pkg_resources.resource_string(__name__, path)
        return data.decode("utf8")

    # TO-DO: change this view to display your data your own way.
    def student_view(self, context=None):
        """
        The primary view of the TimelineXBlock, shown to students
        when viewing courses.
        """
        html = self.resource_string("static/html/mit_cre_timeline.html")
        frag = Fragment(html.format(self=self))
        frag.add_css(self.resource_string("static/css/custom.css"))
        frag.add_css(self.resource_string("static/css/reset.css"))
        frag.add_css(self.resource_string("static/css/style.css"))
        frag.add_css(self.resource_string("static/css/kelly_slab.css"))
        frag.add_javascript(self.resource_string("static/js/src/mit_cre_timeline.js"))
        frag.add_javascript(self.resource_string("static/js/src/jquery.easing.1.3.js"))
        frag.add_javascript(self.resource_string("static/js/src/modernizr.custom.11333.js"))
        frag.initialize_js('TimelineXBlock')
        return frag

    def studio_view(self, context):
        """
        Create a fragment used to display the edit view in the Studio.
        """
        html_str = pkg_resources.resource_string(__name__, "static/html/studio_view.html")
        frag = Fragment(unicode(html_str).format(display_name=self.display_name))
        js_str = pkg_resources.resource_string(__name__, "static/js/src/studio_edit.js")
        frag.add_javascript(unicode(js_str))
        frag.initialize_js('StudioEdit')

        return frag

    @XBlock.json_handler
    def studio_submit(self, data, suffix=''):
        """
        Called when submitting the form in Studio.
        """
        self.display_name = data.get('display_name')

        return {'result': 'success'}


    # TO-DO: change this to create the scenarios you'd like to see in the
    # workbench while developing your XBlock.
    @staticmethod
    def workbench_scenarios():
        """A canned scenario for display in the workbench."""
        return [
            ("TimelineXBlock",
             """<mit_cre_timeline/>
             """),
        ]
