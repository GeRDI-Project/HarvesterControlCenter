# import base64

__author__ = "Jan Frömberg"
__copyright__ = "Copyright 2018, GeRDI Project"
__credits__ = ["Jan Frömberg"]
__license__ = "Apache 2.0"
__maintainer__ = "Jan Frömberg"
__email__ = "Jan.froemberg@tu-dresden.de"


class HarvesterApi:
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
