from rest_framework.response import Response
from rest_framework import status
from requests.exceptions import ConnectionError
import requests
from .harvester_api import Harvester_API

__author__ = "Jan Frömberg"
__copyright__ = "Copyright 2018, GeRDI Project"
__credits__ = ["Jan Frömberg"]
__license__ = "Apache"
__version__ = "1.0.0"
__maintainer__ = "Jan Frömberg"
__email__ = "Jan.froemberg@tu-dresden.de"

class Helpers():
    """Custom helper class."""

    def harvester_response_wrapper(harvester, request_type):
        """Return a harvester response."""
        feedback = {}

        if harvester.enabled == True:
            try:
                if request_type == 'GET':
                    response = requests.get('http://' + harvester.url + Harvester_API.G_STATUS, stream=True)
                    feedback[harvester.name] = response.text# + ' ' + str(response.status_code))
                    if response.status_code == status.HTTP_404_NOT_FOUND:
                        feedback[harvester.name] = 'offline'
                elif request_type == 'POST':
                    response = requests.post('http://' + harvester.url + Harvester_API.P_HARVEST, stream=True)
                    feedback[harvester.name] = response.raw# + ' ' + str(response.status_code))
                    if response.status_code == status.HTTP_404_NOT_FOUND:
                        feedback[harvester.name] = 'offline'

                else:
                    response = Response('no handle')

            except ConnectionError as e:
                response = Response(harvester.name + ' has a Connection Error', status=status.HTTP_408_REQUEST_TIMEOUT)
                feedback[harvester.name] = response.data # + ' ' + str(response.status_code))

            return Response(feedback, status=response.status_code)

        else:
            return Response({harvester.name : 'disabled'}, status=status.HTTP_423_LOCKED)
