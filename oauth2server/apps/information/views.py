from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from rest_framework import status
from django.conf import settings
import logging

stdlogger = logging.getLogger(__name__)





class InformationView(APIView):

    def get(self, request):
        #TODO The get should be supplied to provide introspection for admin functions
        stdlogger.debug(" Hitting HTTP GET analytics view. Application name set as: {}. Application version is set as: {}".format(settings.APPLICATION_NAME, settings.APPLICATION_VERSION))

        return Response(data=settings.MICRO_SERVICE_INFO, status=status.HTTP_200_OK,)
