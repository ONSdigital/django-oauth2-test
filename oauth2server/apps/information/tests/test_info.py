import base64

from rest_framework.test import APIClient
from rest_framework import status
from django.test import TestCase
from django.conf import settings


class InformationViewTest(TestCase):

    def setUp(self):
        self.api_client = APIClient()

    def test_info_endpoint_ok(self):

        response = self.api_client.get(path='/info/',)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['branch'], settings.MICRO_SERVICE_INFO['branch'])
        self.assertEqual(response.data['commit'], settings.MICRO_SERVICE_INFO['commit'])
        self.assertEqual(response.data['origin'], settings.MICRO_SERVICE_INFO['origin'])
        self.assertEqual(response.data['name'], settings.MICRO_SERVICE_INFO['name'])
        self.assertEqual(response.data['version'], settings.MICRO_SERVICE_INFO['version'])


    def test_info_endpoint_post(self):

        # HTTP Post is not allowed
        response = self.api_client.post(path='/info/',)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


    def test_info_endpoint_put(self):

        # HTTP Put is not allowed
        response = self.api_client.put(path='/info/',)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


    def test_info_endpoint_delete(self):

        # HTTP Put is not allowed
        response = self.api_client.delete(path='/info/',)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
