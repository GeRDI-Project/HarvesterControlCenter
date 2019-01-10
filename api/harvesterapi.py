import requests
import logging
import json
from requests.exceptions import ConnectionError
from rest_framework import status
from rest_framework.response import Response

from api.harvesterApiStrategy import HarvesterApiStrategy, VersionBased6Strategy, VersionBased7Strategy

__author__ = "Jan Frömberg"
__copyright__ = "Copyright 2018, GeRDI Project"
__credits__ = ["Jan Frömberg"]
__license__ = "Apache 2.0"
__maintainer__ = "Jan Frömberg"
__email__ = "Jan.froemberg@tu-dresden.de"


class InitHarvesters:
    """

    This Class initializes each harvester and decides the communication protocol to use.

    """

    def __init__(self, harvester):
        self._harvesterVersion = "not defined"
        self.harvester = harvester
        
        if harvester.enabled:
            response = requests.get(harvester.url + "/versions", stream=True)

            if response.status_code == 200:
                harvester_json = json.loads(response.text)
                versionString = harvester_json["value"][1]
                libVersion = versionString.split("-")[2]

                if int(libVersion.split(".")[0]) >= 7:
                    self._harvesterVersion = 7
                else:
                    self._harvesterVersion = 6
            else:
                self._harvesterVersion = "not supported"
        else:
            self._harvesterVersion = "harvester disabled"


    def getVersion(self):
        return self._harvesterVersion
    

    def getHarvesterApi(self):
        v6 = VersionBased6Strategy()
        v7 = VersionBased7Strategy()
        api = HarvesterApiStrategy(self.harvester, v7)
        if self._harvesterVersion == 6:
            api = HarvesterApiStrategy(self.harvester, v6)
        elif self._harvesterVersion == 7:
            api = HarvesterApiStrategy(self.harvester, v7)
        elif self._harvesterVersion == "not supported":
            api = HarvesterApiStrategy(self.harvester, v6)

        return api

