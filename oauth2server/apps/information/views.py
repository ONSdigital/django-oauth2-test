from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from rest_framework import status
from django.utils.decorators import method_decorator
from django.db import IntegrityError, InternalError, DataError, DatabaseError
from django.conf import settings
import logging

stdlogger = logging.getLogger(__name__)


from apps.accounts.decorators import validate_request
from proj.exceptions import DatabaseFailureException



class InformationView(APIView):

    #@method_decorator(validate_request)
    def get(self, request):
        #TODO The get should be supplied to provide introspection for admin functions
        stdlogger.debug(" Hitting HTTP GET analytics view. Application name set as: {}. Application version is set as: {}".format(settings.APPLICATION_NAME, settings.APPLICATION_VERSION))
        data = settings.MICRO_SERVICE_INFO
        # Leave this for future changes and possibly introspection for getting details of a user
        return Response(data=settings.MICRO_SERVICE_INFO, status=status.HTTP_201_CREATED,)

