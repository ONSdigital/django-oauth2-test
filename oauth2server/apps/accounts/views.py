from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils.decorators import method_decorator

from apps.tokens.serializers import OAuthAccessTokenSerializer
from apps.accounts.decorators import validate_request


class AccountView(APIView):

    @method_decorator(validate_request)
    def post(self, request, *args, **kwargs):
        print "hitting post account view"
        #access_token = factory(request=request).grant()
        return Response(data={"name":"nherriot@email.com", "id":"0001","status":"deactivated"}, status=status.HTTP_201_CREATED,)

    @method_decorator(validate_request)
    def get(self, request):
        print "hitting get account view"

        return Response(data={"name":"nherriot@email.com", "id":"0001","status":"deactivated"}, status=status.HTTP_201_CREATED,)



def hello_world(request):
    print "hello world"

    return("hello world")