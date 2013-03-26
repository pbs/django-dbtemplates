

from django.test import TestCase
from dbtemplates.utils.regex_replace import regex_replace

class TestITSRename(TestCase):

    def test1(self):
        content_initial = """
        {% load blabla, its_image_resize, bla %}
        its_image_resize
        <a class="blog-entry-thumbnail" href="{{ entry_prefix_url }}?id={{ entry.id }}">
          <img src='{{ entry.thumbnail|its_image_resize:"165x" }}'
           alt="{{ entry.title }}"/>
        </a>
        {{ entry.thumbnail|its_image_resize: }} -- here there is no width and height
        {{ entry.thumbnail|its_image_resize:"165" }} -- here there is no x
        {{ entry.thumbnail|its_image_resize "165" }} -- here there is no :
        {{ entry.thumbnail its_image_resize:"165x" }} -- here there is no |
        { entry.thumbnail|its_image_resize:"165x" }} -- here there is no starting {
        entry.thumbnail|its_image_resize:"165x" }} -- here there is no starting {{
        """

        content_migrated = """
        {% load blabla, image_resize, bla %}
        its_image_resize
        <a class="blog-entry-thumbnail" href="{{ entry_prefix_url }}?id={{ entry.id }}">
          <img src='{{ entry.thumbnail|image_resize:"165x" }}'
           alt="{{ entry.title }}"/>
        </a>
        {{ entry.thumbnail|its_image_resize: }} -- here there is no width and height
        {{ entry.thumbnail|its_image_resize:"165" }} -- here there is no x
        {{ entry.thumbnail|its_image_resize "165" }} -- here there is no :
        {{ entry.thumbnail its_image_resize:"165x" }} -- here there is no |
        { entry.thumbnail|its_image_resize:"165x" }} -- here there is no starting {
        entry.thumbnail|its_image_resize:"165x" }} -- here there is no starting {{
        """

        self.assertEquals(content_migrated,
                        regex_replace(content_initial, "its_image_resize", "image_resize"))
