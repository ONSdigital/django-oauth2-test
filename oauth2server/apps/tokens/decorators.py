import base64
import re
import logging

from functools import wraps

from django.utils.decorators import available_attrs
from django.conf import settings

from apps.credentials.models import (
    OAuthClient,
    OAuthUser,
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
    UserAccountNotVerified,
    InvalidUserCredentialsException,
    AuthorizationCodeNotFoundException,
    RefreshTokenNotFoundException,
)

stdlogger = logging.getLogger(__name__)


def authentication_required(scope):
    """
    Validates access token and priviliges before processing the view
    :param func:
    :return: decorator
    """
    def _check_access_token_in_header(request):
        if not 'HTTP_AUTHORIZATION' in request.META:
            return False

        # Only Bearer tokens are supported for now
        auth_header = request.META['HTTP_AUTHORIZATION']
        auth_method, auth = re.split(':|;|,| ', auth_header)
        #auth_method, auth = request.META['HTTP_AUTHORIZATION'].split(' ')
        if auth_method.lower() != 'bearer':
            return False

        return auth

    def _check_access_token_in_post(request):
        if 'access_token' not in request.POST:
            return False

        return request.POST['access_token']

    def _check_access_token_in_get(request):
        if 'access_token' not in request.GET:
            return False

        return request.GET['access_token']

    def decorator(func):
        @wraps(func, assigned=available_attrs(func))
        def inner(request, *args, **kwargs):

            access_token = _check_access_token_in_header(request=request)
            if not access_token:
                access_token = _check_access_token_in_post(request=request)
            if not access_token:
                access_token = _check_access_token_in_get(request=request)

            if not access_token:
                raise AccessTokenRequiredException()

            try:
                access_token = OAuthAccessToken.objects.get(
                    access_token=access_token)
            except OAuthAccessToken.DoesNotExist:
                raise InvalidAccessTokenException()

            if access_token.is_expired():
                raise ExpiredAccessTokenException()

            if scope not in access_token.scope:
                raise InsufficientScopeException()

            request.access_token = access_token
            return func(request, *args, **kwargs)

        return inner

    return decorator


def validate_request(func):
    """
    Validates that request contains all required data
    :param func:
    :return: decorator
    """
    stdlogger.debug("Token validate request decorator being called")

    def _validate_grant_type(request):
        """
        Checks grant_type parameter and also performs checks on additional
        parameters required by specific grant types.
        Assigns grant_type to the request so we can use it later.

        Also optionally assigns other objects based on specific grant such
        as user, auth_code and refresh_token
        :param request:
        :return:
        """

        grant_type = request.POST.get('grant_type', None)

        if not grant_type:
            raise GrantTypeRequiredException()

        valid_grant_types = (
            'client_credentials',
            'authorization_code',
            'password',
            'refresh_token',
        )
        if grant_type not in valid_grant_types:
            stdlogger.warning( "Invalid grant type exception" )
            raise InvalidGrantTypeException()

        # authorization_code grant requires code parameter
        if grant_type == 'authorization_code':
            stdlogger.debug("Grant_type auth_code")
            try:
                auth_code = request.POST['code']
            except KeyError:
                try:
                    auth_code = request.GET['code']
                except KeyError:
                    raise CodeRequiredException()

        # password grant requires username and password parameters
        if grant_type == 'password':

            stdlogger.debug("Grant_type password")
            try:
                username = request.POST['username']
            except KeyError:
                try:
                    username = request.GET['username']
                except KeyError:
                    raise UsernameRequiredException()
            try:
                password = request.POST['password']
            except KeyError:
                try:
                    password = request.GET['password']
                except KeyError:
                    raise PasswordRequiredException()

        # refresh_token grant requires refresh_token parameter
        if grant_type == 'refresh_token':
            stdlogger.debug("Grant_type refresh_code")
            try:
                refresh_token = request.POST['refresh_token']
            except KeyError:
                try:
                    refresh_token = request.GET['refresh_token']
                except KeyError:
                    raise RefreshTokenRequiredException()

        if grant_type == 'authorization_code':
            stdlogger.debug("Grant_type auth_code")
            try:
                request.auth_code = OAuthAuthorizationCode.objects.get(
                    code=auth_code)
            except OAuthAuthorizationCode.DoesNotExist:
                raise AuthorizationCodeNotFoundException()

        if grant_type == 'password':

            stdlogger.debug("Grant_type password. Second function")

            try:
                user = OAuthUser.objects.get(email=username)
            except OAuthUser.DoesNotExist:
                stdlogger.warning( "Raised InvalidUserCredentialsException")
                raise InvalidUserCredentialsException()

            if not user.verify_password(password):
                stdlogger.debug("I've raised InvalidUserCredentialsException - password failed the check!")
                user.increment_failed_logins()
                user.save()
                if user.get_failed_logins() >= settings.MAX_FAILED_LOGINS:
                    user.lock_account()
                    user.save()
                    raise UserAccountLockedException()
                raise InvalidUserCredentialsException()

            if not user.account_is_verified:
                stdlogger.warning("Raised UserAccountNotVerified")
                raise UserAccountNotVerified()

            if user.account_locked():
                stdlogger.warning("Raised UserAccountLockedException")
                raise UserAccountLockedException()

            user.reset_failed_logins()
            user.unlock_account()
            user.save()
            request.user = user

        if grant_type == 'refresh_token':
            stdlogger.debug( "This is grant_type refresh_code. Second function")
            try:
                request.refresh_token = OAuthRefreshToken.objects.get(
                    refresh_token=refresh_token)
            except OAuthRefreshToken.DoesNotExist:
                raise RefreshTokenNotFoundException()

        request.grant_type = grant_type

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
            stdlogger.debug("*** We have a HTTP_AUTHORIZATION request ***")
            auth_header = request.META['HTTP_AUTHORIZATION']

            try:
                auth_method, auth = re.split(':|;|,| ', auth_header)
            #auth_method, auth = request.META['HTTP_AUTHORIZATION'].split(':')
            except ValueError as http_auth_header_error:
                stdlogger.warning("http auth header looks corrupt: {}".format(auth_header))
                raise InvalidClientCredentialsException()

            if auth_method.lower() == 'basic':
                client_id, client_secret = base64.b64decode(auth).split(':')

        # Fallback to POST and then to GET
        if not client_id or not client_secret:
            stdlogger.info("Client id is missing from GET, trying POST")
            try:
                client_id = request.POST['client_id']
                client_secret = request.POST['client_secret']
            except KeyError:
                try:
                    client_id = request.GET['client_id']
                    client_secret = request.GET['client_secret']
                except KeyError:
                    stdlogger.warning("The client_id and client_secret in a POST and GET method is missing")
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

    def _extract_scope(request):
        """
        Tries to extract authorization scope from the request.
        Appropriate scope models are fetched from the database
        and assigned to the request.
        :param request:
        :return:
        """
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
        stdlogger.debug("Decorator called for Validating OAuth2 requests")
        _validate_grant_type(request=request)
        _extract_client(request=request)
        _extract_scope(request=request)

        return func(request, *args, **kwargs)

    return decorator
