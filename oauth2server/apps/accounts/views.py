from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from rest_framework import status
from django.utils.decorators import method_decorator
from django.db import IntegrityError, InternalError, DataError, DatabaseError

from apps.tokens.serializers import OAuthAccessTokenSerializer
from apps.accounts.decorators import validate_request


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
        print "hitting post account view"
        print "User object is: ", request.user

        # Try and persist the user to the DB. Remember this could fail a data integrity check if some other system has
        # saved this user before we run this line of code!
        try:
            request.user.save()

        except (IntegrityError, InternalError, DataError, DatabaseError):
            # The chances of this happening are slim to none! And this line of code should never happen. So we really
            # need to tell the other system we are not capable of creating the resource.
            raise DatabaseFailureException

        context ={'account': request.user.email, 'created': 'success'}
        print context
        json_context = JSONRenderer().render(context)

        print json_context
        return Response(data=json_context, status=status.HTTP_201_CREATED,)

    @method_decorator(validate_request)
    def get(self, request):
        print "hitting get account view"

        return Response(data={"name":"nherriot@email.com", "id":"0001","status":"deactivated"}, status=status.HTTP_201_CREATED,)



def hello_world(request):
    print "hello world"

    return("hello world")