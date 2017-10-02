import base64

from rest_framework.test import APIClient
from rest_framework import status
from django.test import TestCase

class UserAdministrationTest(TestCase):

    fixtures = ['test_credentials',]

    def setUp(self):
        self.api_client = APIClient()

    # Make sure that client_id with admin privilege can't update the account if it's in a locked state.
    # Use john3@doe.com which has a locked account
    def test_locked_account(self):
        response = self.api_client.put(
            path='/api/account/create/',
            data={
                'client_id': 'testclient',
                'client_secret': 'testpassword',
                'username': 'john3@doe.com',
                'password': 'newpassword',
                'account_verified': 'true'
            },
            HTTP_AUTHORIZATION='Basic:{}'.format(
                base64.encodestring('testclient:testpassword')),
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], u'User account locked')

    # Make sure that a client_id with admin privilege can change the users password
    def test_update_password_success(self):
        response = self.api_client.put(
            path='/api/account/create/',
            data={
                'client_id': 'testclient',
                'client_secret': 'testpassword',
                'username': 'john@doe.com',
                'password': 'testpassword',
                'account_verified': 'true'
            },
            HTTP_AUTHORIZATION='Basic:{}'.format(
                base64.encodestring('testclient:testpassword')),
        )

        # Expected response should be like: {"account":"john@doe.com","updated":"success"}
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

