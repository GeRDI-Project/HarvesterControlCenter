# import base64
import abc

__author__ = "Jan Frömberg"
__copyright__ = "Copyright 2018, GeRDI Project"
__credits__ = ["Jan Frömberg"]
__license__ = "Apache 2.0"
__maintainer__ = "Jan Frömberg"
__email__ = "Jan.froemberg@tu-dresden.de"


class HarvesterApiConstants:
    """

     This Class holds a list of Harvester API constants which will be updated accordingly to the Harvester-BaseLibrary.
     Current version is 7.x.x See: https://wiki.gerdi-project.de/display/GeRDI/Harvester+Library+7.x.x
     
    """
    PG_HARVEST = "/"
    P_HARVEST_ABORT = "/abort"
    P_HARVEST_RESET = "/reset"
    G_HARVEST_LOG = "/log"
    P_HARVEST_CRON = "/harvest/schedule/_add" #E.g. {"cronTab" : "0 0 * * *"}
    G_HARVEST_CRON = "/harvest/schedule"
    D_HARVEST_CRON = "/harvest/schedule/_delete" #E.g. {"cronTab" : "0 0 * * *"}
    DALL_HARVEST_CRON = "/harvest/schedule/_deleteAll"
    G_HEALTH = "/health"
    G_BOOLEAN_OUTDATED = "/outdated"

    # HARVESTER_USER = ""
    # HARVESTER_PASS = ""
    # credentials = base64.b64encode(HARVESTER_USER + ':' + HARVESTER_PASS)

class HarvesterApi:
    """
    Define the interface of interest to clients.
    Maintain a reference to a Strategy object.
    """

    def __init__(self, strategy):
        self._strategy = strategy

    def HarvesterApi_interface(self):
        self._strategy.getHarvest_interface()


class Strategy(metaclass=abc.ABCMeta):
    """
    Declare an interface common to all supported algorithms. HarvesterApi
    uses this interface to call the algorithm defined by a
    ConcreteStrategy.
    """

    @abc.abstractmethod
    def getHarvest_interface(self):
        pass


class VersionBased6(Strategy):
    """
    Implement the algorithm using the Strategy interface.
    """

    def getHarvest_interface(self):
        pass


class VersionBased7(Strategy):
    """
    Implement the algorithm using the Strategy interface.
    """

    def getHarvest_interface(self):
        pass

# usage
    v7 = VersionBased7()
    context = HarvesterApi(v7)
    context.getHarvest_interface()