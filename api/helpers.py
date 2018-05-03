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
                    feedback[harvester.name] = {}
                    response = requests.get(harvester.url + Harvester_API.G_STATUS, stream=True)
                    feedback[harvester.name]['status'] = response.text
                    response = requests.get(harvester.url + Harvester_API.G_HARVESTED_DOCS, stream=True)
                    feedback[harvester.name]['cached_docs'] = response.text
                    response = requests.get(harvester.url + Harvester_API.G_DATA_PROVIDER, stream=True)
                    feedback[harvester.name]['data_pvd'] = response.text
                    response = requests.get(harvester.url + Harvester_API.G_MAX_DOCS, stream=True)
                    feedback[harvester.name]['max_docs'] = response.text
                    response = requests.get(harvester.url + Harvester_API.G_HEALTH, stream=True)
                    feedback[harvester.name]['health'] = response.text
                    response = requests.get(harvester.url + Harvester_API.G_PROGRESS, stream=True)
                    feedback[harvester.name]['progress'] = response.text
                    if "N" not in response.text:
                        feedback[harvester.name]['progress_cur'] = 100 / int(response.text.split("/")[0])
                        if "/" not in response.text:
                            feedback[harvester.name]['progress_max'] = int(response.text.split("/")[0])
                        else:
                            feedback[harvester.name]['progress_max'] = response.text.split("/")[1]
                            feedback[harvester.name]['progress_cur'] = (response.text.split("/")[1] / int(response.text.split("/")[0])) + 100

                    if response.status_code == status.HTTP_404_NOT_FOUND:
                        feedback[harvester.name] = 'offline'
                elif request_type == 'POST':
                    response = requests.post(harvester.url + Harvester_API.P_HARVEST, stream=True)
                    feedback[harvester.name] = response.text
                    if response.status_code == status.HTTP_404_NOT_FOUND:
                        feedback[harvester.name] = 'offline'
                else:
                    response = Response('no method given')
            except ConnectionError as e:
                response = Response("A Connection Error. Host probably down.", status=status.HTTP_408_REQUEST_TIMEOUT)
                feedback[harvester.name] = response.status_text + '. ' + response.data
            return Response(feedback, status=response.status_code)
        else:
            return Response({harvester.name : 'disabled'}, status=status.HTTP_423_LOCKED)
