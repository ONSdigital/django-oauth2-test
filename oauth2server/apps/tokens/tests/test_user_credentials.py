import base64

from rest_framework.test import APIClient
from rest_framework import status
from django.test import TestCase

from apps.credentials.models import OAuthUser
from apps.tokens.models import OAuthAccessToken, OAuthRefreshToken


class UserCredentialsTest(TestCase):

    fixtures = [
        'test_credentials',
        'test_scopes',
    ]

    def setUp(self):
        self.api_client = APIClient()
        self.assertEqual(OAuthAccessToken.objects.count(), 0)
        self.assertEqual(OAuthRefreshToken.objects.count(), 0)

    def test_missing_client_credentials(self):
        response = self.api_client.post(
            path='/api/v1/tokens/',
            data={
                'grant_type': 'password',
                'username': 'john@doe.com',
                'password': 'testpassword',
            },
        )

        self.assertEqual(OAuthAccessToken.objects.count(), 0)
        self.assertEqual(OAuthRefreshToken.objects.count(), 0)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], u'Client credentials were not found in the headers or body')

    def test_invalid_client_credentials(self):
        response = self.api_client.post(
            path='/api/v1/tokens/',
            data={
                'grant_type': 'password',
                'username': 'john@doe.com',
                'password': 'testpassword',
            },
            HTTP_AUTHORIZATION='Basic:{}'.format(
                base64.encodestring('bogus:bogus')),
        )

        self.assertEqual(OAuthAccessToken.objects.count(), 0)
        self.assertEqual(OAuthRefreshToken.objects.count(), 0)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], u'Invalid client credentials')

    def test_corrupt_client_credentials(self):
        response = self.api_client.post(
            path='/api/v1/tokens/',
            data={
                'grant_type': 'password',
                'username': 'john@doe.com',
                'password': 'testpassword',
            },
            HTTP_AUTHORIZATION='Basic: ,;{}'.format(
                base64.encodestring('bogus:bogus;wrong')),
        )

        self.assertEqual(OAuthAccessToken.objects.count(), 0)
        self.assertEqual(OAuthRefreshToken.objects.count(), 0)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], u'Invalid client credentials')

    # This uses a user that does not exist in the database
    def test_account_does_not_exist(self):
        response = self.api_client.post(
            path='/api/v1/tokens/',
            data={
                'grant_type': 'password',
                'username': 'wrong@user.com',
                'password': 'testpassword',
            },
            HTTP_AUTHORIZATION='Basic:{}'.format(
                base64.encodestring('testclient:testpassword')),
        )

        self.assertEqual(OAuthAccessToken.objects.count(), 0)
        self.assertEqual(OAuthRefreshToken.objects.count(), 0)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], u'Unauthorized user credentials!!!')

    # This uses the john@doe.com user with the wrong password
    def test_account_wrong_password(self):
        response = self.api_client.post(
            path='/api/v1/tokens/',
            data={
                'grant_type': 'password',
                'username': 'john@doe.com',
                'password': 'wrong password',
            },
            HTTP_AUTHORIZATION='Basic:{}'.format(
                base64.encodestring('testclient:testpassword')),
        )

        self.assertEqual(OAuthAccessToken.objects.count(), 0)
        self.assertEqual(OAuthRefreshToken.objects.count(), 0)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], u'Unauthorized user credentials!!!')

    # This uses the john2@doe.com account to test a user who has not had his account verified.
    def test_account_not_verified(self):
        response = self.api_client.post(
            path='/api/v1/tokens/',
            data={
                'grant_type': 'password',
                'username': 'john2@doe.com',
                'password': 'testpassword',
            },
            HTTP_AUTHORIZATION='Basic:{}'.format(
                base64.encodestring('testclient:testpassword')),
        )

        self.assertEqual(OAuthAccessToken.objects.count(), 0)
        self.assertEqual(OAuthRefreshToken.objects.count(), 0)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], u'User account not verified')

    # This uses the john3@doe.com account to test a user who has a verified account but is locked.
    def test_account_is_locked(self):
        response = self.api_client.post(
            path='/api/v1/tokens/',
            data={
                'grant_type': 'password',
                'username': 'john3@doe.com',
                'password': 'testpassword',
            },
            HTTP_AUTHORIZATION='Basic:{}'.format(
                base64.encodestring('testclient:testpassword')),
        )

        self.assertEqual(OAuthAccessToken.objects.count(), 0)
        self.assertEqual(OAuthRefreshToken.objects.count(), 0)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], u'User account locked')

    # This uses the john3@doe.com account to test a user with wrong details who is locked
    def test_account_is_locked_wrong_password(self):
        response = self.api_client.post(
            path='/api/v1/tokens/',
            data={
                'grant_type': 'password',
                'username': 'john3@doe.com',
                'password': 'wrongpassword',
            },
            HTTP_AUTHORIZATION='Basic:{}'.format(
                base64.encodestring('testclient:testpassword')),
        )

        self.assertEqual(OAuthAccessToken.objects.count(), 0)
        self.assertEqual(OAuthRefreshToken.objects.count(), 0)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], u'Unauthorized user credentials!!!')

    # This uses the john4@doe.com account has 9 failed logins. We need to test if we use the wrong password again
    # it will lock the user account from obtaining a token.
    def test_account_is_locked_after_10_requests(self):
        response = self.api_client.post(
            path='/api/v1/tokens/',
            data={
                'grant_type': 'password',
                'username': 'john4@doe.com',
                'password': 'wrongpassword',
            },
            HTTP_AUTHORIZATION='Basic:{}'.format(
                base64.encodestring('testclient:testpassword')),
        )

        self.assertEqual(OAuthAccessToken.objects.count(), 0)
        self.assertEqual(OAuthRefreshToken.objects.count(), 0)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], u'User account locked')

        locked_user = OAuthUser.objects.get(email='john4@doe.com')
        self.assertEqual(locked_user.account_locked(), True)

    def test_should_login_with_different_case_email(self):
        # Given
        data = {
            'grant_type': 'password',
            'username': 'John@Doe.com',
            'password': 'testpassword'
        }

        # When
        response = self.api_client.post(
            path='/api/v1/tokens/',
            data=data,
            HTTP_AUTHORIZATION='Basic:{}'.format(
                base64.encodestring('testclient:testpassword')),
        )

        # Then
        self.assertEqual(OAuthAccessToken.objects.count(), 1, 'Should have issued an access token')
        self.assertEqual(OAuthRefreshToken.objects.count(), 1, 'Should have issued a refresh token')

        access_token, refresh_token = OAuthAccessToken.objects.last(), OAuthRefreshToken.objects.last()

        self.assertEqual(access_token.client.client_id, 'testclient')
        self.assertEqual(access_token.user.email, 'john@doe.com')
        self.assertEqual(access_token.refresh_token, refresh_token)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_success(self):
        response = self.api_client.post(
            path='/api/v1/tokens/',
            data={
                'grant_type': 'password',
                'username': 'john@doe.com',
                'password': 'testpassword',
            },
            HTTP_AUTHORIZATION='Basic:{}'.format(
                base64.encodestring('testclient:testpassword')),
        )

        self.assertEqual(OAuthAccessToken.objects.count(), 1)
        self.assertEqual(OAuthRefreshToken.objects.count(), 1)
        access_token = OAuthAccessToken.objects.last()
        refresh_token = OAuthRefreshToken.objects.last()

        self.assertEqual(access_token.client.client_id, 'testclient')
        self.assertEqual(access_token.user.email, 'john@doe.com')
        self.assertEqual(access_token.refresh_token, refresh_token)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['id'], access_token.pk)
        self.assertEqual(response.data['access_token'], access_token.access_token)
        self.assertEqual(response.data['expires_in'], 3600)
        self.assertEqual(response.data['token_type'], 'Bearer')
        self.assertIn('qux', response.data['scope'])
        self.assertIn('foo', response.data['scope'])
        self.assertIn('bar', response.data['scope'])
        self.assertEqual(response.data['refresh_token'], refresh_token.refresh_token)
