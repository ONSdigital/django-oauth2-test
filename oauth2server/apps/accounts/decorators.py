import base64
import re

from functools import wraps
from django.core.validators import validate_email
from django.conf import settings

import logging

stdlogger = logging.getLogger(__name__)

from apps.credentials.models import (
    OAuthClient,
    OAuthUser,
    ValidationError,
)
from apps.tokens.models import (
    OAuthScope,
)
from proj.exceptions import (
    UsernameRequiredException,
    PasswordRequiredException,
    ClientCredentialsRequiredException,
    InvalidClientCredentialsException,
    UserAccountLockedException,
    InvalidUserCredentialsException,
    DuplicateUserException,
    UnknownUserException,
)


def validate_request(func):
    """
    Validates that request contains all required data for creating, updating and deleting an OAuth User account. It
    looks for a valid client and client_id. It then validates the username and password for size and duplicate accounts.
    If scope parameters are given they will be set if part of the system.
    If account active is set, the account will be set as active, otherwise it will be set as deactivated.
    :param func:
    :return: decorator
    """

    stdlogger.info("Validate request decorator being called")

    def _extract_client(request):
        """
        Tries to extract the client_id & client_secret from the HTTP Message.
        The parameters are all mandatory for POST,PUT,GET and DELETE

        Assigns client object to the request for later use.
        :param request:
        :return request:
        """

        client_id, client_secret = None, None

        # First, let's check Authorization header if present
        # TODO - Look at removing this and encrypting password. It's an OAuth2 server, so it should be over SSL anyway
        # but revisit this if time permits.
        if 'HTTP_AUTHORIZATION' in request.META:
            stdlogger.debug("We have a HTTP_AUTHORIZATION request ***")
            auth_header = request.META['HTTP_AUTHORIZATION']
            auth_method, auth = re.split(':|;|,| ', auth_header)
            if auth_method.lower() == 'basic':
                client_id, client_secret = base64.b64decode(auth).split(':')

        if request.method == 'POST':
            try:
                client_id = request.POST['client_id']
                client_secret = request.POST['client_secret']
            except KeyError:
                stdlogger.warning("Client ID and Client Secret is missing from the POST method")
                raise ClientCredentialsRequiredException()

        if request.method == 'PUT':
            try:
                client_id = request.POST['client_id']
                client_secret = request.POST['client_secret']
            except KeyError:
                stdlogger.warning("Client ID and Client Secret is missing from the PUT method")
                raise ClientCredentialsRequiredException()

        if request.method == 'GET':
            try:
                client_id = request.GET['client_id']
                client_secret = request.GET['client_secret']
            except KeyError:
                stdlogger.warning("Client ID and Client Secret is missing from the GET method")
                raise ClientCredentialsRequiredException()

        if request.method == 'DELETE':
            try:
                client_id = request.POST['client_id']
                client_secret = request.POST['client_secret']
            except KeyError:
                stdlogger.warning("Client ID and Client Secret is missing from the DELETE method")
                raise ClientCredentialsRequiredException()

        # Check client exists
        try:
            client = OAuthClient.objects.get(client_id=client_id)
        except OAuthClient.DoesNotExist:
            raise InvalidClientCredentialsException()

        # And that client secret is correct
        if not client.verify_password(client_secret):
            raise InvalidClientCredentialsException()

        request.client = client

    def _extract_username(request, **kwargs):
        """
        Tries to extract the user_id & password from the HTTP Message.
        The user_id is mandatory for POST,PUT,GET and DELETE.
        The password is mandatory for POST but optional for PUT, GET and DELETE.
        It is effectively ignored for everything but POST

        Assigns client object to the request for later use.
        :param request:
        :return request:
        """

        stdlogger.debug(" In _extract_username method for validating a request")

        username, password = None, None

        if request.method == 'POST':
            try:
                username = request.POST['username']
                validate_email(username)
            except KeyError:
                stdlogger.warning("Username is missing from the POST method")
                raise UsernameRequiredException()
            except ValidationError:
                stdlogger.warning("email failed validation check for validating a user")
                raise InvalidUserCredentialsException

            try:
                password = request.POST['password']
            except KeyError:
                stdlogger.warning("Password is missing from the POST method")
                raise PasswordRequiredException()

            # For a POST message we are creating a new user. Make sure this email is unique!
            try:
                # Try create an OAuthUser object and validate that it's unique. Hence we just instantiate the object.
                user = OAuthUser(email=username, password=password, account_is_verified=False)
                user.validate_unique()
            except ValidationError:
                stdlogger.warning(
                    "We failed username check for creating a user in the HTTP POST. This user already exists")
                raise DuplicateUserException

        if request.method == 'PUT':
            try:
                username = request.POST['username']
                validate_email(username)
                user = OAuthUser.objects.get(email=username)
            except KeyError:
                stdlogger.warning("Username is missing from the PUT method")
                raise UsernameRequiredException()
            except ValidationError:
                stdlogger.warning("Email failed validation check for validating a user")
                raise InvalidUserCredentialsException
            except OAuthUser.DoesNotExist:
                stdlogger.error(
                    "Error while updating the User ID. The email does not exist on the OAuth2 server")
                raise UnknownUserException

            try:
                # If we are changing the users ID, we need to check he is not over-writing a different user
                new_username = request.POST['new_username']
                validate_email(new_username)
                check_user = OAuthUser.objects.get(email=new_username)
                if check_user:
                    stdlogger.warning(
                        "The respondent has tried to change their email to an already active email address")
                    raise DuplicateUserException

            except KeyError:
                # We don't do anything if a new_user is not specified as it is optional. So set it to none.
                stdlogger.info("This PUT method does not specify a new user.")
                request.new_username = None
            except ValidationError:
                stdlogger.warning("Email failed validation check for validating a user")
                raise InvalidUserCredentialsException
            except OAuthUser.DoesNotExist:
                # This is not an error. We actually want the new_user variable to not be used in our DB. It means it's
                # not used. Hence we can use the new name to change the current user ID to the new name! Thimpless :-)
                request.new_username = new_username

            try:
                password = request.POST['password']
                user.password = password
            except KeyError:
                # If password is missing then it's not changing so set it as none. This is an optional parm
                stdlogger.info("Password is missing from the PUT method of a user.")
                pass

        # We can ignore even detecting the 'password' in the GET as it's not used.
        if request.method == 'GET':
            try:
                username = request.GET['username']
                validate_email(username)
                user = OAuthUser.objects.get(email=username)
            except KeyError:
                stdlogger.warning("Username is missing from the GET method")
                raise UsernameRequiredException()
            except ValidationError:
                stdlogger.warning("Email failed validation check for validating a user")
                raise InvalidUserCredentialsException
            except OAuthUser.DoesNotExist:
                stdlogger.error(
                    "Error while getting the User ID. The email does not exist on the OAuth2 server")
                raise UnknownUserException

        # We can ignore even detecting the 'password' in the DELETE as it's not used.
        if request.method == 'DELETE':
            try:
                username = request.POST['username']
                validate_email(username)
                user = OAuthUser.objects.get(email=username)
            except KeyError:
                stdlogger.warning("Username is missing from the DELETE method")
                raise UsernameRequiredException()
            except ValidationError:
                stdlogger.warning("Email failed validation check for validating a user")
                raise InvalidUserCredentialsException
            except OAuthUser.DoesNotExist:
                stdlogger.error(
                    "Error while trying to DELETE the User. The email does not exist on the OAuth2 server")
                raise UnknownUserException

        # OK we pass all validation checks pass the user object back in the request
        request.user = user

    def _extract_active(request):
        stdlogger.info("Extracting account verified flag")

        """
        Tries to extract the account verified flag from the HTTP Message.
        If it is a POST the attribute is optional - defaults to False when created.
        If it is a PUT the attribute is optional - defaults to the current value.
        If it is a GET / DELETE it is optional - has no effect on result and not used in query 
        
        Assigns client object to the request for later use.
        :param request:
        :return request:
        """

        if request.method == 'POST':
            try:
                account_verified = request.POST['account_verified']
                if account_verified == u'true':
                    request.user.account_is_verified = True
                if account_verified == u'false':
                    request.user.account_is_verified = False
            except KeyError:
                # This is an optional parameter so set it as false if it is not present
                request.user.account_is_verified = False
                pass

        if request.method == 'PUT':
            try:
                account_verified = request.POST['account_verified']
                if account_verified == u'true':
                    request.user.account_is_verified = True
                if account_verified == u'false':
                    request.user.account_is_verified = False
            except KeyError:
                pass

    def _extract_scope(request):
        """
        Tries to extract authorization scope from the request.
        Appropriate scope models are fetched from the database
        and assigned to the request.
        :param request:
        :return:
        """

        stdlogger.info("Running Extracting scope method from the request to validate a user")

        if request.grant_type not in ('client_credentials', 'password'):
            return

        if settings.OAUTH2_SERVER['IGNORE_CLIENT_REQUESTED_SCOPE']:
            request.scopes = OAuthScope.objects.filter(is_default=True)
            return

        try:
            scopes = request.POST['scope'].split(' ')
        except KeyError:
            try:
                scopes = request.GET['scope'].split(' ')
            except KeyError:
                scopes = []

        request.scopes = OAuthScope.objects.filter(scope__in=scopes)

        # Fallback to the default scope if no scope sent with the request
        if len(request.scopes) == 0:
            request.scopes = OAuthScope.objects.filter(is_default=True)

    def _extract_account_locked(request):
        # TODO add in the detecting of this attribute
        pass

    def _extract_failed_logins(request):
        # TODO add in the detecting of this attribute
        pass

    def decorator(request, *args, **kwargs):
        stdlogger.debug("decorator is hit for administration REST interface...")

        _extract_client(request=request)
        _extract_username(request=request, *args, **kwargs)
        _extract_active(request=request)

        return func(request, *args, **kwargs)

    return decorator
