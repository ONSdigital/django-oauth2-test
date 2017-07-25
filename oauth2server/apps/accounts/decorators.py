import base64
import re
from functools import wraps

from django.utils.decorators import available_attrs
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
    OAuthAuthorizationCode,
    OAuthAccessToken,
    OAuthRefreshToken,
    OAuthScope,
)
from proj.exceptions import (
    GrantTypeRequiredException,
    InvalidGrantTypeException,
    CodeRequiredException,
    UsernameRequiredException,
    PasswordRequiredException,
    RefreshTokenRequiredException,
    AccessTokenRequiredException,
    InvalidAccessTokenException,
    ExpiredAccessTokenException,
    InsufficientScopeException,
    ClientCredentialsRequiredException,
    InvalidClientCredentialsException,
    UserAccountLockedException,
    InvalidUserCredentialsException,
    AuthorizationCodeNotFoundException,
    RefreshTokenNotFoundException,
    DuplicateUserException,
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
        Tries to extract client_id and client_secret from the request.
        It first looks for Authorization header, then tries POST data.
        Assigns client object to the request for later use.
        :param request:
        :return:
        """
        client_id, client_secret = None, None



        # First, let's check Authorization header if present
        if 'HTTP_AUTHORIZATION' in request.META:
            stdlogger.debug("We have a HTTP_AUTHORIZATION request ***")
            auth_header = request.META['HTTP_AUTHORIZATION']
            auth_method, auth = re.split(':|;|,| ', auth_header)
            #auth_method, auth = request.META['HTTP_AUTHORIZATION'].split(':')
            if auth_method.lower() == 'basic':
                client_id, client_secret = base64.b64decode(auth).split(':')

        # Fallback to POST and then to GET
        if not client_id or not client_secret:
            stdlogger.info("Hit client check for a missing variable")
            try:
                client_id = request.POST['client_id']
                client_secret = request.POST['client_secret']
            except KeyError:
                try:
                    client_id = request.GET['client_id']
                    client_secret = request.GET['client_secret']
                except KeyError:
                    stdlogger.warning("Client ID and Client Secret is missing from the POST and GET method")
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
        Tries to extract username and password from the request.
        It first looks for Authorization header, then tries POST data.
        Assigns client object to the request for later use.
        It checks kwargs to see if this is an:
            admin 'add',
            admin 'set active',
            admin 'set password' or
            admin 'set active'

        :param request, **kwargs:
        :return request:
        """

        stdlogger.debug(" In _extract_username method for validating a request")

        username, password = None, None

        try:
            username = request.POST['username']
        except KeyError:
            try:
                username = request.GET['username']
            except KeyError:
                raise UsernameRequiredException()

        try:
            validate_email(username)

        except ValidationError:
            stdlogger.warning("email failed validation check for validating a user")
            raise InvalidUserCredentialsException

        stdlogger.debug("***** validation check kwargs are: {} *****".format(kwargs))
        #stdlogger.debug("***** validation check args are: {} *****".format(args))
        try:
            password = request.POST['password']
        except KeyError:
            try:
                password = request.GET['password']
                stdlogger.debug("password found from HTTP GET")
            except KeyError:
                raise PasswordRequiredException()

        # Check username does not exist in the DB
        try:
            # Try create an OAuthUser object and validate that it's unique. Hence we just instantiate the object.
            stdlogger.debug("Trying to create user")
            user = OAuthUser(email=username, password=password, account_is_verified=False)
            user.validate_unique()

        except ValidationError:
            stdlogger.warning( "we failed username check for creating a user")
            raise DuplicateUserException

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
                request.user.account_is_verified = account_verified
                stdlogger.debug("Extracting account verified flag successful")
            except KeyError:
                # This is an optional parameter so set it as false if it is not present
                request.user.account_is_verified = False


        if request.method == 'GET':
            try:
                account_verified = request.GET['account_verified']
                request.user.account_is_verified = account_verified
            except KeyError:
                # This is an optional parameter so set it as false if it is not present
                pass


        if request.method == 'PUT':
            try:
                account_verified = request.PUT['account_verified']
                request.user.account_is_verified = account_verified
            except KeyError:
                # This is an optional parameter so set it as false if it is not present
                request.user.account_is_verified = False


        if request.method == 'DELETE':
            try:
                account_verified = request.DELETE['account_verified']
                request.user.account_is_verified = account_verified
            except KeyError:
                # This is an optional parameter so set it as false if it is not present
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

    def decorator(request, *args, **kwargs):
        stdlogger.debug("decorator is hit for administration REST interface...")

        if request.method == 'GET':
            stdlogger.debug("***** decorator method hit! .... This is a HTTP GET message")
        if request.method == 'POST':
            stdlogger.debug("***** decorator method hit! .... This is a HTTP POST message")
        if request.method == 'PUT':
            stdlogger.debug("***** decorator method hit! .... This is a HTTP PUT message")
        if request.method == 'DELETE':
            stdlogger.debug("***** decorator method hit! .... This is a HTTP DELETE message")


        _extract_client(request=request)
        _extract_username(request=request, *args, **kwargs)
        _extract_active(request=request)
        #_extract_scope(request=request)

        return func(request, *args, **kwargs)

    return decorator

