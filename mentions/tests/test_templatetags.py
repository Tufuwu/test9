from django.urls import reverse

from mentions.tasks import outgoing_webmentions
from mentions.tests import WebmentionTestCase
from mentions.tests.util import testfunc


class TemplateTagTests(WebmentionTestCase):
    def test_webmention_endpoint_templatetag(self):
        expected_endpoint = testfunc.endpoint_submit_webmention()
        response = self.client.get(reverse("test-template-tags"))

        self.assertTemplateUsed(response, "templatetags_example.html")
        self.assertContains(response, expected_endpoint)
        print(response.content)

        self.assertEqual(
            outgoing_webmentions._get_endpoint_in_html(response.content),
            expected_endpoint,
        )
