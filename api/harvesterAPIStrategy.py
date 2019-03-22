import abc
import requests
import logging
import json
import datetime
from requests.exceptions import ConnectionError, Timeout, RequestException
from rest_framework import status
from rest_framework.response import Response

from api.constants import HarvesterApiConstantsV6, HarvesterApiConstantsV7
from api.constants import HCCJSONConstants as HCCJC

__author__ = "Jan Frömberg"
__copyright__ = "Copyright 2018, GeRDI Project"
__credits__ = ["Jan Frömberg"]
__license__ = "Apache 2.0"
__maintainer__ = "Jan Frömberg"
__email__ = "jan.froemberg@tu-dresden.de"


# Get an instance of a logger
logger = logging.getLogger(__name__)


class Strategy(metaclass=abc.ABCMeta):
    """
    Declare an interface common to all supported algorithms. HarvesterApi
    uses this interface to call the algorithm defined by a
    ConcreteStrategy.
    Each method must return a Response with a JSON Body (see HCC Constants)
    """

    @abc.abstractmethod
    def get_harvesterStatus(self, harvester):
        pass

    @abc.abstractmethod
    def get_harvesterLog(self, harvester):
        pass

    @abc.abstractmethod
    def post_startHarvest(self, harvester):
        pass

    @abc.abstractmethod
    def post_stopHarvest(self, harvester):
        pass

    @abc.abstractmethod
    def post_resetHarvest(self, harvester):
        pass
    
    @abc.abstractmethod
    def get_harvesterLog(self, harvester):
        pass

    @abc.abstractmethod
    def post_addHarvesterSchedule(self, harvester, crontab):
        pass

    @abc.abstractmethod
    def post_deleteHarvesterSchedule(self, harvester, crontab):
        pass

    @abc.abstractmethod
    def get_harvesterProgress(self, harvester):
        pass


class HarvesterApiStrategy:
    """
    Define the interface of interest to clients.
    Maintain a reference to a Strategy object.
    """

    def __init__(self, harvester, strategy):
        self._strategy = strategy
        self.harvester = harvester

    def set_strategy(self, strategy):
        self._strategy = strategy
    
    def get_harvester(self):
        return self.harvester

    def harvesterStatus(self):
        return self._strategy.get_harvesterStatus(self.harvester)

    def startHarvest(self):
        logger.info(self.harvester.name + " start clicked by user.")
        return self._strategy.post_startHarvest(self.harvester)

    def stopHarvest(self):
        logger.info(self.harvester.name + " stop clicked by user.")
        return self._strategy.post_stopHarvest(self.harvester)

    def resetHarvest(self):
        logger.info(self.harvester.name + " reset clicked by user.")
        return self._strategy.post_resetHarvest(self.harvester)
    
    def harvesterLog(self):
        return self._strategy.get_harvesterLog(self.harvester)

    def addSchedule(self, crontab):
        logger.info(self.harvester.name + " scheduled added by user.")
        return self._strategy.post_addHarvesterSchedule(self.harvester, crontab)
    
    def deleteSchedule(self, crontab):
        logger.info(self.harvester.name + " schedules deleted by user.")
        return self._strategy.post_deleteHarvesterSchedule(self.harvester, crontab)

    def harvesterProgress(self):
        return self._strategy.get_harvesterProgress(self.harvester)


class BaseStrategy(Strategy):
    """
    Fallback strategy alorithm for basic harvester support.
    Just UP/DOWN information.
    """
    def get_harvesterStatus(self, harvester):
        feedback = {}
        response = None
        if harvester.enabled:
            try:
                feedback[harvester.name] = {}
                response = requests.get(harvester.url, timeout=5)

                if response.status_code == status.HTTP_401_UNAUTHORIZED:
                    feedback[harvester.name][HCCJC.HEALTH] = 'Authentication required.'
                    feedback[harvester.name][HCCJC.GUI_STATUS] = HCCJC.WARNING
                    return Response(feedback, status=status.HTTP_401_UNAUTHORIZED)

                if response.status_code == status.HTTP_404_NOT_FOUND:
                    feedback[harvester.name][HCCJC.HEALTH] = 'Resource on server not found. Check URL.'
                    feedback[harvester.name][HCCJC.GUI_STATUS] = HCCJC.WARNING
                    return Response(feedback, status=status.HTTP_404_NOT_FOUND)

                if response.status_code == status.HTTP_200_OK:
                    feedback[harvester.name][HCCJC.HEALTH] = response.text
                    feedback[harvester.name][HCCJC.GUI_STATUS] = HCCJC.SUCCESS

                feedback[harvester.name][HCCJC.CRONTAB] = "cron not supported. basic mode."

            except RequestException as e:
                feedback[harvester.name][HCCJC.HEALTH] = str(e)
                feedback[harvester.name][HCCJC.GUI_STATUS] = HCCJC.WARNING

            return Response(feedback, status=response.status_code if response is not None else status.HTTP_408_REQUEST_TIMEOUT)
        else:
            # logging.debug("Harvester disabled - got no info; returning a Response with JSON")
            return Response({harvester.name: 'disabled'}, status=status.HTTP_423_LOCKED)

    def post_startHarvest(self, harvester):
        return Response({harvester.name : 'start not supported'}, status=status.HTTP_501_NOT_IMPLEMENTED)

    def post_resetHarvest(self, harvester):
        return Response({harvester.name : 'reset not supported'}, status=status.HTTP_501_NOT_IMPLEMENTED)

    def post_stopHarvest(self, harvester):
        return Response({harvester.name : 'stop not supported'}, status=status.HTTP_501_NOT_IMPLEMENTED)

    def get_harvesterLog(self, harvester):
        return Response({harvester.name : {HCCJC.LOGS : 'log not supported'}}, status=status.HTTP_501_NOT_IMPLEMENTED)

    def get_harvesterProgress(self, harvester):
        return Response({harvester.name : {HCCJC.PROGRESS : 'progress not supported'}}, status=status.HTTP_501_NOT_IMPLEMENTED)

    def post_addHarvesterSchedule(self, harvester, crontab):
        return Response({harvester.name : {HCCJC.HEALTH : 'cron not supported'}}, status=status.HTTP_501_NOT_IMPLEMENTED)
    
    def post_deleteHarvesterSchedule(self, harvester, crontab):
        return Response({harvester.name : {HCCJC.HEALTH : 'cron not supported'}}, status=status.HTTP_501_NOT_IMPLEMENTED)


class VersionBased6Strategy(Strategy):
    """
    Implement the algorithm using the Strategy interface.
    """

    def a_response(self, harvester_name, url, method):
        feedback = {}
        feedback[harvester_name] = {}
        response = None
        if method == 'Get':
            try:
                feedback[harvester_name] = {}
                response = requests.get(url, timeout=5)
                feedback[harvester_name] = response.text
            except RequestException as e:
                feedback[harvester_name][HCCJC.HEALTH] = str(e)
                feedback[harvester_name][HCCJC.GUI_STATUS] = HCCJC.WARNING

            return Response(feedback, status=response.status_code if response is not None else status.HTTP_408_REQUEST_TIMEOUT)
        elif method == 'Put':
            try:
                feedback[harvester_name] = {}
                response = requests.put(url, timeout=5)
                feedback[harvester_name] = response.text
            except RequestException as e:
                feedback[harvester_name][HCCJC.HEALTH] = str(e)
                feedback[harvester_name][HCCJC.GUI_STATUS] = HCCJC.WARNING

            return Response(feedback, status=response.status_code if response is not None else status.HTTP_408_REQUEST_TIMEOUT)
        elif method == 'Post':
            try:
                feedback[harvester_name] = {}
                response = requests.post(url, timeout=9)
                feedback[harvester_name] = response.text
            except RequestException as e:
                feedback[harvester_name][HCCJC.HEALTH] = str(e)
                feedback[harvester_name][HCCJC.GUI_STATUS] = HCCJC.WARNING

            return Response(feedback, status=response.status_code if response is not None else status.HTTP_408_REQUEST_TIMEOUT)

        return Response(feedback, status=status.HTTP_400_BAD_REQUEST)
    
    def get_harvesterStatus(self, harvester):
        feedback = {}
        response = None
        if harvester.enabled:
            try:
                feedback[harvester.name] = {}
                response = requests.get(harvester.url + HarvesterApiConstantsV6.G_STATUS, timeout=5)

                if response.status_code == status.HTTP_401_UNAUTHORIZED:
                    feedback[harvester.name][HCCJC.HEALTH] = 'Authentication required.'
                    feedback[harvester.name][HCCJC.GUI_STATUS] = HCCJC.WARNING
                    return Response(feedback, status=status.HTTP_401_UNAUTHORIZED)

                if response.status_code == status.HTTP_404_NOT_FOUND:
                    feedback[harvester.name][HCCJC.HEALTH] = 'Resource on server not found. Check URL.'
                    feedback[harvester.name][HCCJC.GUI_STATUS] = HCCJC.WARNING
                    return Response(feedback, status=status.HTTP_404_NOT_FOUND)

                feedback[harvester.name][HCCJC.STATUS] = response.text
                response = requests.get(harvester.url + HarvesterApiConstantsV6.G_HARVESTED_DOCS, timeout=5)
                feedback[harvester.name][HCCJC.CACHED_DOCS] = response.text

                response = requests.get(harvester.url + HarvesterApiConstantsV6.G_DATA_PROVIDER, timeout=5)
                feedback[harvester.name][HCCJC.DATA_PROVIDER] = response.text

                response = requests.get(harvester.url + HarvesterApiConstantsV6.G_MAX_DOCS, timeout=5)
                feedback[harvester.name][HCCJC.MAX_DOCUMENTS] = response.text

                response = requests.get(harvester.url + HarvesterApiConstantsV6.G_HEALTH, timeout=5)
                feedback[harvester.name][HCCJC.HEALTH] = response.text

                if feedback[harvester.name][HCCJC.HEALTH] == HCCJC.OK and feedback[harvester.name][HCCJC.STATUS] == 'idling':
                    feedback[harvester.name][HCCJC.GUI_STATUS] = HCCJC.SUCCESS

                elif feedback[harvester.name][HCCJC.HEALTH] != HCCJC.OK:
                    feedback[harvester.name][HCCJC.GUI_STATUS] = HCCJC.WARNING

                elif feedback[harvester.name][HCCJC.STATUS].lower() == 'initialization':
                    feedback[harvester.name][HCCJC.GUI_STATUS] = HCCJC.PRIMARY

                else:
                    feedback[harvester.name][HCCJC.GUI_STATUS] = HCCJC.INFO

                response = requests.get(harvester.url + HarvesterApiConstantsV6.G_PROGRESS, timeout=5)
                feedback[harvester.name][HCCJC.PROGRESS] = response.text
                if response.status_code != status.HTTP_500_INTERNAL_SERVER_ERROR:
                    feedback[harvester.name][HCCJC.PROGRESS_CURRENT] = feedback[harvester.name][HCCJC.CACHED_DOCS]
                    if "/" not in response.text:
                        feedback[harvester.name][HCCJC.PROGRESS_MAX] = int(response.text)
                    elif "N/A" not in response.text:
                        feedback[harvester.name][HCCJC.PROGRESS_MAX] = int(response.text.split("/")[1])
                        feedback[harvester.name][HCCJC.PROGRESS_CURRENT] = \
                            int((int(response.text.split("/")[0]) / int(response.text.split("/")[1])) * 100)

                response = requests.get(harvester.url + HarvesterApiConstantsV6.GD_HARVEST_CRON, timeout=5)
                crontab = "Schedules:"
                cron = response.text.find(crontab)
                cronstring = response.text[cron + 11:cron + 11 + 9]
                if cronstring[0] == '-':
                    cronstring = 'no crontab defined yet'
                feedback[harvester.name][HCCJC.CRONTAB] = cronstring

            except RequestException as e:
                feedback[harvester.name][HCCJC.HEALTH] = str(e)
                feedback[harvester.name][HCCJC.GUI_STATUS] = HCCJC.WARNING

            return Response(feedback, status=response.status_code if response is not None else status.HTTP_408_REQUEST_TIMEOUT)
        else:
            # logging.debug("Harvester disabled - got no info; returning a Response with JSON")
            return Response({harvester.name: 'disabled'}, status=status.HTTP_423_LOCKED)

    def post_startHarvest(self, harvester):
        if harvester.enabled:
            return self.a_response(harvester.name, harvester.url + HarvesterApiConstantsV6.P_HARVEST, 'Post')
        else:
            return Response({harvester.name: 'disabled'}, status=status.HTTP_423_LOCKED)

    def post_resetHarvest(self, harvester):
        if harvester.enabled:
            return self.a_response(harvester.name, harvester.url + HarvesterApiConstantsV6.P_HARVEST_RESET, 'Post')
        else:
            return Response({harvester.name: 'disabled'}, status=status.HTTP_423_LOCKED)
    
    def post_stopHarvest(self, harvester):
        if harvester.enabled:
            return self.a_response(harvester.name, harvester.url + HarvesterApiConstantsV6.P_HARVEST_ABORT, 'Post')
        else:
            return Response({harvester.name : {HCCJC.HEALTH : 'disabled'}}, status=status.HTTP_423_LOCKED)

    def get_harvesterLog(self, harvester):
        return Response({harvester.name : {HCCJC.LOGS : 'not implemented'}}, status=status.HTTP_501_NOT_IMPLEMENTED)

    def get_harvesterProgress(self, harvester):
        return Response({harvester.name : {HCCJC.PROGRESS : 'not implemented'}}, status=status.HTTP_501_NOT_IMPLEMENTED)

    def post_addHarvesterSchedule(self, harvester, crontab):
        feedback = {}
        feedback[harvester.name] = {}
        del_response = requests.delete(harvester.url + HarvesterApiConstantsV6.GD_HARVEST_CRON, timeout=5)
        response = requests.post(harvester.url + HarvesterApiConstantsV6.PD_HARVEST_CRON + crontab, timeout=5)
        feedback[harvester.name][HCCJC.HEALTH] = del_response.text + ', ' + response.text
        return Response(feedback, status=response.status_code)

    def post_deleteHarvesterSchedule(self, harvester, crontab):
        feedback = {}
        feedback[harvester.name] = {}
        if crontab:
            response = requests.delete(harvester.url + HarvesterApiConstantsV6.PD_HARVEST_CRON + crontab, timeout=5)
            feedback[harvester.name][HCCJC.HEALTH] = response.text
        else:
            response = requests.delete(harvester.url + HarvesterApiConstantsV6.GD_HARVEST_CRON, timeout=5)
            feedback[harvester.name][HCCJC.HEALTH] = response.text
        return Response(feedback, status=response.status_code)


class VersionBased7Strategy(Strategy):
    """

    Implement the algorithm for the harvester lib v7.x.x using the Strategy interface.

    """

    def a_response(self, harvester_name, url, method):
        feedback = {}
        feedback[harvester_name] = {}
        response = None

        try:

            if method == 'Get':
                response = requests.get(url, timeout=5)
            elif method == 'Put':
                response = requests.put(url, timeout=5)
            elif method == 'Post':
                response = requests.post(url, timeout=9)
            elif method == 'Delete':
                response = requests.delete(url, timeout=5)

            try:    
                harvester_json = json.loads(response.text)

                if HCCJC.STATUS in harvester_json:
                    feedback[harvester_name][HCCJC.STATUS] = harvester_json[HCCJC.STATUS]
                    feedback[harvester_name][HCCJC.STATE] = harvester_json[HCCJC.STATUS]

                if HCCJC.MESSAGE in harvester_json:
                    feedback[harvester_name][HCCJC.HEALTH] = harvester_json[HCCJC.MESSAGE]

            except ValueError:
                harvester_json = response.text
                feedback[harvester_name] = harvester_json

        except RequestException as e:

            feedback[harvester_name][HCCJC.HEALTH] = str(e)
            feedback[harvester_name][HCCJC.GUI_STATUS] = HCCJC.WARNING

        return Response(feedback, status=response.status_code if response is not None else status.HTTP_408_REQUEST_TIMEOUT), harvester_json

    def get_harvesterStatus(self, harvester):
        feedback = {}
        maxDocuments = False
        response = None

        if harvester.enabled:
            try:
                feedback[harvester.name] = {}
                response, x = self.a_response(harvester.name, harvester.url + HarvesterApiConstantsV7.PG_HARVEST, 'Get')
                harvester_json = x
                
                if response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE:
                    feedback[harvester.name][HCCJC.HEALTH] = harvester_json[HCCJC.MESSAGE]
                    feedback[harvester.name][HCCJC.GUI_STATUS] = HCCJC.PRIMARY
                    feedback[harvester.name][HCCJC.STATUS] = HCCJC.INIT
                    feedback[harvester.name][HCCJC.STATE] = harvester_json[HCCJC.STATUS]
                elif response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR:
                    feedback[harvester.name][HCCJC.HEALTH] = harvester_json[HCCJC.MESSAGE]
                    feedback[harvester.name][HCCJC.GUI_STATUS] = HCCJC.WARNING
                    feedback[harvester.name][HCCJC.STATUS] = harvester_json[HCCJC.STATUS]
                    feedback[harvester.name][HCCJC.STATE] = harvester_json[HCCJC.STATUS]
                elif response.status_code == status.HTTP_401_UNAUTHORIZED:
                    feedback[harvester.name][HCCJC.HEALTH] = response.status_text
                    feedback[harvester.name][HCCJC.GUI_STATUS] = HCCJC.WARNING
                else:

                    feedback[harvester.name][HCCJC.HEALTH] = harvester_json[HCCJC.HEALTH]
                    # to be legacy (prior lib v7) compatible in html template set the old STATUS to STATE
                    feedback[harvester.name][HCCJC.STATUS] = harvester_json[HCCJC.STATE].lower()
                    feedback[harvester.name][HCCJC.CACHED_DOCS] = harvester_json[HCCJC.HARVESTED_COUNT]
                    feedback[harvester.name][HCCJC.PROGRESS] = harvester_json[HCCJC.HARVESTED_COUNT]
                    feedback[harvester.name][HCCJC.DATA_PROVIDER] = harvester_json[HCCJC.REPO_NAME]

                    if harvester_json[HCCJC.HEALTH] == HCCJC.OK and harvester_json[HCCJC.STATE].lower() == HCCJC.IDLE:
                        feedback[harvester.name][HCCJC.GUI_STATUS] = HCCJC.SUCCESS
                    elif harvester_json[HCCJC.HEALTH] != HCCJC.OK:
                        feedback[harvester.name][HCCJC.GUI_STATUS] = HCCJC.WARNING
                    elif harvester_json[HCCJC.STATE].lower() in [HCCJC.HARV]:
                        feedback[harvester.name][HCCJC.GUI_STATUS] = HCCJC.PRIMARY
                    else:
                        feedback[harvester.name][HCCJC.GUI_STATUS] = HCCJC.INFO

                    if HCCJC.MAX_DOCUMENT_COUNT in harvester_json:
                        maxDocuments = True
                        feedback[harvester.name][HCCJC.MAX_DOCUMENTS] = harvester_json[HCCJC.MAX_DOCUMENT_COUNT]
                        feedback[harvester.name][HCCJC.PROGRESS_MAX] = harvester_json[HCCJC.MAX_DOCUMENT_COUNT]
                    else:
                        feedback[harvester.name][HCCJC.MAX_DOCUMENTS] = HCCJC.N_A

                    if maxDocuments:
                        if int(harvester_json[HCCJC.MAX_DOCUMENT_COUNT]) > 0:
                            feedback[harvester.name][HCCJC.PROGRESS_CURRENT] = \
                            int((int(harvester_json[HCCJC.HARVESTED_COUNT]) * 100) / int(harvester_json[HCCJC.MAX_DOCUMENT_COUNT]))
                    else:
                        feedback[harvester.name][HCCJC.PROGRESS_CURRENT] = int(harvester_json[HCCJC.HARVESTED_COUNT])
                    
                    if HCCJC.LAST_HARVEST_DATE in harvester_json:
                        feedback[harvester.name][HCCJC.LAST_HARVEST_DATE] = harvester_json[HCCJC.LAST_HARVEST_DATE]
                    if HCCJC.NEXT_HARVEST_DATE in harvester_json:
                        feedback[harvester.name][HCCJC.NEXT_HARVEST_DATE] = harvester_json[HCCJC.NEXT_HARVEST_DATE]
                    if HCCJC.REMAIN_HARVEST_TIME in harvester_json:
                        feedback[harvester.name][HCCJC.REMAIN_HARVEST_TIME] = harvester_json[HCCJC.REMAIN_HARVEST_TIME]

                    # schedules
                    response, x = self.a_response(harvester.name, harvester.url + HarvesterApiConstantsV7.G_HARVEST_CRON, 'Get')
                    harvester_json = x
                    if not harvester_json[HCCJC.SCHEDULE]:
                        feedback[harvester.name][HCCJC.CRONTAB] = HCCJC.NO_CRONTAB
                    else:
                        feedback[harvester.name][HCCJC.CRONTAB] = harvester_json[HCCJC.SCHEDULE]

            except RequestException as e:
                feedback[harvester.name][HCCJC.HEALTH] = str(e)
                feedback[harvester.name][HCCJC.GUI_STATUS] = HCCJC.WARNING
            
            return Response(feedback, status=response.status_code if response is not None else status.HTTP_408_REQUEST_TIMEOUT)
        else:
            return Response({harvester.name: 'disabled'}, status=status.HTTP_423_LOCKED)

    def post_startHarvest(self, harvester):
        response, x = self.a_response(harvester.name, harvester.url + HarvesterApiConstantsV7.PG_HARVEST, 'Post')
        return response

    def post_resetHarvest(self, harvester):
        response, x = self.a_response(harvester.name, harvester.url + HarvesterApiConstantsV7.P_HARVEST_RESET, 'Post')
        return response
    
    def post_stopHarvest(self, harvester):
        response, x = self.a_response(harvester.name, harvester.url + HarvesterApiConstantsV7.P_HARVEST_ABORT, 'Post')
        return response

    def get_harvesterLog(self, harvester):
        now = datetime.datetime.now()
        feedback = {}
        feedback[harvester.name] = {}
        response, json = self.a_response(harvester.name, harvester.url + HarvesterApiConstantsV7.G_HARVEST_LOG 
            + now.strftime(HarvesterApiConstantsV7.HARVESTER_LOG_FORMAT), 'Get')
        
        feedback[harvester.name][HCCJC.LOGS] = str(json) if str(json) != "" else HCCJC.NO_LOGTEXT + ' for today: ' + str(now)
        return Response(feedback, status=response.status_code)

    def get_harvesterProgress(self, harvester):
        feedback = {}
        feedback[harvester.name] = {}
        maxDocuments = False
        
        if harvester.enabled:
            
            response, x = self.a_response(harvester.name, harvester.url + HarvesterApiConstantsV7.PG_HARVEST, 'Get')
            harvester_json = x

            feedback[harvester.name][HCCJC.PROGRESS] = harvester_json[HCCJC.HARVESTED_COUNT]
            feedback[harvester.name][HCCJC.STATE] = harvester_json[HCCJC.STATE].lower()
            if HCCJC.MAX_DOCUMENT_COUNT in harvester_json:
                maxDocuments = True
                feedback[harvester.name][HCCJC.MAX_DOCUMENTS] = harvester_json[HCCJC.MAX_DOCUMENT_COUNT]
                feedback[harvester.name][HCCJC.PROGRESS_MAX] = harvester_json[HCCJC.MAX_DOCUMENT_COUNT]
            else:
                feedback[harvester.name][HCCJC.MAX_DOCUMENTS] = HCCJC.N_A
            
            if HCCJC.REMAIN_HARVEST_TIME in harvester_json:
                feedback[harvester.name][HCCJC.REMAIN_HARVEST_TIME] = harvester_json[HCCJC.REMAIN_HARVEST_TIME]
            
            if maxDocuments:
                if int(harvester_json[HCCJC.MAX_DOCUMENT_COUNT]) > 0:
                    feedback[harvester.name][HCCJC.PROGRESS_CURRENT] = \
                    int((int(harvester_json[HCCJC.HARVESTED_COUNT]) * 100) / int(harvester_json[HCCJC.MAX_DOCUMENT_COUNT]))
            else:
                feedback[harvester.name][HCCJC.PROGRESS_CURRENT] = int(harvester_json[HCCJC.HARVESTED_COUNT])

        return Response(feedback, status=response.status_code)

    def post_addHarvesterSchedule(self, harvester, crontab):
        feedback = {}
        feedback[harvester.name] = {}
        response = requests.post(harvester.url + 
        HarvesterApiConstantsV7.P_HARVEST_CRON, json={HCCJC.POSTCRONTAB : crontab}, timeout=5)
        harvester_response = response.text
        feedback[harvester.name][HCCJC.HEALTH] = harvester_response
        return Response(feedback, status=response.status_code)
    
    def post_deleteHarvesterSchedule(self, harvester, crontab):
        feedback = {}
        feedback[harvester.name] = {}
        if not crontab:
            response = requests.post(harvester.url + 
            HarvesterApiConstantsV7.DALL_HARVEST_CRON, timeout=5)
            harvester_response = response.text
            feedback[harvester.name][HCCJC.HEALTH] = harvester_response
        else:
            response = requests.post(harvester.url + 
            HarvesterApiConstantsV7.D_HARVEST_CRON, json={HCCJC.POSTCRONTAB : crontab}, timeout=5)
            harvester_response = response.text
            feedback[harvester.name][HCCJC.HEALTH] = harvester_response
        return Response(feedback, status=response.status_code)

