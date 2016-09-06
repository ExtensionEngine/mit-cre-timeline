"""TO-DO: Write a description of what this XBlock is."""

import pkg_resources

from xblock.core import XBlock
from xblock.fields import Scope, Integer, String
from xblock.fragment import Fragment
from functools import partial
from webob.response import Response
from xmodule.contentstore.content import StaticContent
from xmodule.contentstore.django import contentstore


class TimelineXBlock(XBlock):
    """
    This XBlock shows pretty jQuery powered timeline HTML page.
    It currently has no input except edit display_name in edX studio
    but future plans include a form where content author would be able
    to create their own timeline.
    """

    # Fields are defined on the class.  You can access them in your code as
    # self.<fieldname>.
    display_description = String(help="XBlock subtitle", default=None, scope=Scope.content)
    thumbnail_url = String(help="URL of the thumbnail image", default=None, scope=Scope.content)

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
        frag.add_css_url(
            self.runtime.local_resource_url(
                self, 'public/css/custom.css'))
        frag.add_css_url(
            self.runtime.local_resource_url(
                self, 'public/css/reset.css'))
        frag.add_css_url(
            self.runtime.local_resource_url(
                self, 'public/css/style.css'))
        frag.add_css_url(
            self.runtime.local_resource_url(
                self, 'public/css/kelly_slab.css'))
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
        frag = Fragment(unicode(html_str).format(
            display_name=self.display_name,
            thumbnail_url=self.thumbnail_url,
            display_description=self.display_description
        ))
        js_str = pkg_resources.resource_string(__name__, "static/js/src/studio_edit.js")
        frag.add_javascript(unicode(js_str))
        frag.initialize_js('StudioEdit')

        return frag

    @XBlock.handler
    def studio_submit(self, request, suffix=''):
        """
        Called when submitting the form in Studio.
        """
        data = request.POST
        self.display_name = data['display_name']
        self.display_description = data['display_description']

        if not isinstance(data['thumbnail'], basestring):
            upload = data['thumbnail']

            filename = self._file_storage_name(upload.file.name)
            content_location = StaticContent.compute_location(self.location.course_key, filename)

            chunked = upload.file.multiple_chunks()
            sc_partial = partial(StaticContent, content_location, filename, upload.file.content_type)
            if chunked:
                content = sc_partial(upload.file.chunks())
                tempfile_path = upload.file.temporary_file_path()
            else:
                content = sc_partial(upload.file.read())
                tempfile_path = None

            contentstore().save(content)

            # readback the saved content - we need the database timestamp
            readback = contentstore().find(content.location)
            locked = getattr(content, 'locked', False)
            self.thumbnail_url = StaticContent.serialize_asset_key_with_slash(content.location)

        return Response(json_body={'result': 'success'})

    def _file_storage_name(self, filename):
        # pylint: disable=no-member
        """
        Get file path of storage.
        """
        path = (
            '{loc.block_type}/{loc.block_id}'
            '/{filename}'.format(
                loc=self.location,
                filename=filename
            )
        )

        return path

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
