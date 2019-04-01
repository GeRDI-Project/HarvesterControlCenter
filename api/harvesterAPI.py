"""
This module initiaized a harvester and determines its version to decide the protocol language.
"""
import json
import requests
from requests.exceptions import RequestException
from rest_framework import status
from rest_framework.response import Response

from api.harvesterAPIStrategy import HarvesterApiStrategy, BaseStrategy,\
                                     VersionBased6Strategy,\
                                     VersionBased7Strategy
from api.constants import HarvesterApiConstants as HAC

__author__ = "Jan Frömberg"
__copyright__ = "Copyright 2018, GeRDI Project"
__credits__ = ["Jan Frömberg"]
__license__ = "Apache 2.0"
__maintainer__ = "Jan Frömberg"
__email__ = "jan.froemberg@tu-dresden.de"


class InitHarvester:
    """

    This class initializes a harvester and decides the communication protocol to use.
    Therefore it asks the harvester itself which library version it is using.

    """

    def __init__(self, harvester):
        self._harvester_version = "not defined"
        self.harvester = harvester

        if harvester.enabled:
            try:
                response = requests.get(harvester.url + HAC.G_VERSIONS, timeout=5)
            except RequestException as e:
                response = Response("A Connection Error. Harvester initialization failed. "+str(e),
                                    status=status.HTTP_408_REQUEST_TIMEOUT)

            if response.status_code == status.HTTP_401_UNAUTHORIZED:
                response = Response('Authentication required.',
                                    status=status.HTTP_401_UNAUTHORIZED)
            if response.status_code == status.HTTP_404_NOT_FOUND:
                response = Response('Resource on server not found. Check URL.',
                                    status=status.HTTP_404_NOT_FOUND)

            if response.status_code == status.HTTP_200_OK:
                harvester_json = json.loads(response.text)
                version_string = harvester_json["value"][1]
                lib_version = version_string.split("-")[2]

                if int(lib_version.split(".")[0]) >= 7:
                    self._harvester_version = 7
                else:
                    self._harvester_version = 6
            else:
                self._harvester_version = "not supported"
        else:
            self._harvester_version = "harvester disabled"


    def getVersion(self):
        """
        get the harvester Version.
        """
        return self._harvester_version

    def getHarvesterApi(self):
        """
        get the harvester API.
        """
        v6 = VersionBased6Strategy()
        v7 = VersionBased7Strategy()
        api = HarvesterApiStrategy(self.harvester, v7)
        if self._harvester_version == 6:
            api = HarvesterApiStrategy(self.harvester, v6)
        elif self._harvester_version == 7:
            api = HarvesterApiStrategy(self.harvester, v7)
        elif self._harvester_version == "not supported":
            api = HarvesterApiStrategy(self.harvester, BaseStrategy())

        return api
