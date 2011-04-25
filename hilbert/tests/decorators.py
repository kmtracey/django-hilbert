"""
Tests for Django-Hilbert decorators.
"""

from django.conf import settings

from hilbert.tests.base import HilbertBaseTestCase

__all__ = (
    'AjaxLoginRequiredTestCase',
    'AjaxOnlyTestCase',
    'AnonymousRequiredTestCase',
)

class AjaxLoginRequiredTestCase(HilbertBaseTestCase):

    def setUp(self):
        super(AjaxLoginRequiredTestCase, self).setUp()
        self.test_user = self.create_user()
        self.url = '/hilbert/test/ajaxlogin/'

    def test_basic_login_required(self):
        """
        Non-Ajax requests should still be handled with a login-required.
        """

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

        self.client.login(username=self.username, password=self.password)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_ajax_login_required(self):
        """
        Ajax requests should return custom headers to indicate login is required.
        """

        response = self.client.get(self.url, is_ajax=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response['X-Django-Requires-Auth'])
        self.assertEqual(response['X-Django-Login-Url'], settings.LOGIN_URL)

        self.client.login(username=self.username, password=self.password)
        response = self.client.get(self.url, is_ajax=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('X-Django-Requires-Auth' not in response)
        self.assertTrue('X-Django-Login-Url' not in response)


class AjaxOnlyTestCase(HilbertBaseTestCase):

    def setUp(self):
        super(AjaxOnlyTestCase, self).setUp()
        self.url = '/hilbert/test/ajaxonly/'

    def test_non_ajax_requests(self):
        """
        Non-Ajax requests will get a 400 - Bad Request.
        """

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 400)

    def test_ajax_requests(self):
        """
        Ajax requests will get 200 status.
        """

        response = self.client.get(self.url, is_ajax=True)
        self.assertEqual(response.status_code, 200)


class AnonymousRequiredTestCase(HilbertBaseTestCase):

    def setUp(self):
        super(AnonymousRequiredTestCase, self).setUp()
        self.test_user = self.create_user()
        self.basic_url = '/hilbert/test/anonymous/'
        self.custom_url = '/hilbert/test/anonymous-custom/'
        self.custom_target = '/hilbert/test/simple/'

    def test_basic_anonymous_response(self):
        """
        Anonymous users will get the view response.
        """

        response = self.client.get(self.basic_url)
        self.assertEqual(response.status_code, 200)

    def test_custom_anonymous_response(self):
        """
        Anonymous users will get the view response.
        """

        response = self.client.get(self.custom_url)
        self.assertEqual(response.status_code, 200)

    def test_authenticated_response(self):
        """
        Authenticated users will get the redirect: '/' by default
        """

        self.client.login(username=self.username, password=self.password)
        response = self.client.get(self.basic_url)
        self.assertRedirects(response, '/')
        self.client.logout()

    def test_custom_authenticated_response(self):
        """
        Authenticated users will get the redirect url as specified
        """

        self.client.login(username=self.username, password=self.password)
        response = self.client.get(self.custom_url)
        self.assertRedirects(response, self.custom_target)
        self.client.logout()


