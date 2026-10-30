from unittest.mock import patch

from django.test import Client, SimpleTestCase, override_settings
from django.urls import resolve


class UnknownAPIRouteTests(SimpleTestCase):
    def test_unknown_api_routes_return_json_with_debug_on_and_off(self):
        for debug in (True, False):
            with override_settings(DEBUG=debug):
                for path in ('/api', '/api/', '/api/missing/', '/api/profile/wrong-address/', '/api/users/missing/'):
                    with self.subTest(debug=debug, path=path):
                        response = self.client.get(path)
                        self.assertEqual(response.status_code, 404)
                        self.assertEqual(response['Content-Type'], 'application/json')
                        self.assertEqual(response.json(), {'detail': 'API endpoint not found.'})

    def test_unknown_writes_return_json_without_requiring_csrf(self):
        client = Client(enforce_csrf_checks=True)
        for method in ('post', 'put', 'patch', 'delete', 'options'):
            with self.subTest(method=method):
                response = getattr(client, method)('/api/missing/')
                self.assertEqual(response.status_code, 404)
                self.assertEqual(response.json(), {'detail': 'API endpoint not found.'})

    def test_existing_api_routes_keep_their_original_views(self):
        self.assertEqual(resolve('/api/profile/getProfile/').url_name, 'user-profile')
        self.assertEqual(resolve('/api/users/signin/').url_name, 'signin')

    @patch('server.urls.serve_next_frontend')
    def test_unknown_api_route_never_calls_the_frontend(self, frontend):
        self.assertEqual(self.client.get('/api/missing/').status_code, 404)
        frontend.assert_not_called()

    def test_web_routes_still_resolve_to_the_frontend(self):
        for path in ('/', '/accounts/signin/', '/apiary/'):
            self.assertEqual(resolve(path).url_name, 'next-frontend')
