import logging

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from rest_framework import status
from django.utils.decorators import method_decorator
from django.db import IntegrityError, InternalError, DataError, DatabaseError

from apps.accounts.decorators import validate_request
from proj.exceptions import DatabaseFailureException

stdlogger = logging.getLogger(__name__)


class AccountView(APIView):

    @method_decorator(validate_request)
    def post(self, request, *args, **kwargs):
        """
        Take the user object from the request and call the 'save' method on it to persist to the DB. If this succeeds
        then we can report a success.

        :param request:
        :param args:
        :param kwargs:
        :return: Serialised JSON Response Object to indicate the resource has been created
        """
        stdlogger.debug("Hitting HTTP POST account view")

        # Try and persist the user to the DB. Remember this could fail a data integrity check if some other system has
        # saved this user before we run this line of code!
        try:
            request.user.save()

        except (IntegrityError, InternalError, DataError, DatabaseError):
            # The chances of this happening are slim to none! And this line of code should never happen. So we really
            # need to tell the other system we are not capable of creating the resource.
            raise DatabaseFailureException

        context = {'account': request.user.email, 'created': 'success'}
        json_context = JSONRenderer().render(context)

        return Response(data=json_context, status=status.HTTP_201_CREATED, )

    @method_decorator(validate_request)
    def get(self, request):
        # TODO The get should be supplied to provide introspection for admin functions
        stdlogger.debug("Hitting HTTP GET account view")
        # Leave this for future changes and possibly introspection for getting details of a user
        return Response(data={"name": "none", "id": "none", "status": "none"}, status=status.HTTP_201_CREATED, )

    @method_decorator(validate_request)
    def put(self, request):
        """
        Take the user object from the request and updates user info if it exists in the DB. If the email (which is
        unique) is to be updated this will be in a new attribute within the PUT message called new_username.
        If this succeeds then we can report a success.

        :param request:
        :param args:
        :param kwargs:
        :return: Serialised JSON Response Object to indicate the resource has been created
        """

        stdlogger.debug("Hitting HTTP PUT account view")
        # Try and persist the user to the DB. Remember this could fail a data integrity check if some other system has
        # saved this user before we run this line of code!
        # if account_locked attribute set to False, we want to unlock the account
        try:
            # Check to see if the PUT is changing the user ID or the POST contains the account_locked flag.
            # If so we Key and change the email to the new one or unlock account and reset failed log-ins.
            if request.new_username:
                stdlogger.info("Admin is updating a user ID to a new value")
                request.user.email = request.new_username
            if request.POST.get('account_locked') == 'False':
                stdlogger.debug('Admin is unlocking account')
                request.user.unlock_account()
                request.user.reset_failed_logins()
                # Verify user if not verified
                if not request.user.account_is_verified:
                    request.user.verify_account()
            request.user.save()

        except (IntegrityError, InternalError, DataError, DatabaseError):
            # The chances of this happening are slim to none! And this line of code should never happen. So we really
            # need to tell the other system we are not capable of creating the resource.
            raise DatabaseFailureException

        context = {'account': request.user.email, 'updated': 'success'}
        json_context = JSONRenderer().render(context)

        return Response(data=json_context, status=status.HTTP_201_CREATED, )

    @method_decorator(validate_request)
    def delete(self, request):
        """
        Take the user object from the request and call the 'delete' method on it if it exists in the DB.
        If this succeeds then we can report a success.

        :param request:
        :param args:
        :param kwargs:
        :return: Serialised JSON Response Object to indicate the resource has been created
        """

        stdlogger.debug("Hitting HTTP DELETE account view")
        user_email = request.user.email
        try:
            stdlogger.debug("Deleting this user object")
            request.user.delete()
        except (IntegrityError, InternalError, DataError, DatabaseError):
            # The chances of this happening are slim to none! And this line of code should never happen. So we really
            # need to tell the other system we are not capable of creating the resource.
            raise DatabaseFailureException

        context = {'account': user_email, 'deleted': 'success'}
        json_context = JSONRenderer().render(context)

        return Response(data=json_context, status=status.HTTP_201_CREATED, )
