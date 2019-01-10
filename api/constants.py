# import base64

__author__ = "Jan Frömberg"
__copyright__ = "Copyright 2018, GeRDI Project"
__credits__ = ["Jan Frömberg"]
__license__ = "Apache 2.0"
__maintainer__ = "Jan Frömberg"
__email__ = "Jan.froemberg@tu-dresden.de"


class HCCJSONConstants:
    """

     This Class holds a list of Harvester Control Center JSON constants.

    """
    HEALTH = "health"
    GUI_STATUS = "gui_status"
    STATUS = "status"
    STATE = "state"
    CACHED_DOCS = "cached_docs"
    DATA_PROVIDER = "data_pvd"
    MAX_DOCUMENTS = "max_docs"
    MAX_DOCUMENT_COUNT = "maxDocumentCount"
    PROGRESS = "progress"
    PROGRESS_MAX = "progress_max"
    PROGRESS_CURRENT = "progress_cur"
    CRONTAB = "cron"
    LOGS = "log"

    OK = "OK"

    WARNING = "warning"
    SUCCESS = "success"
    PRIMARY = "primary"
    INFO = "info"


class HarvesterApiConstantsV6:
    """

     This Class holds a list of Harvester API constants which will be updated accordingly to the Harvester-BaseLibrary.

    """
    P_HARVEST = "/"
    P_HARVEST_ABORT = "/abort"
    P_HARVEST_RESET = "/reset"
    P_HARVEST_SUBMIT = "/submit"
    P_HARVEST_SAVE = "/save"
    PD_HARVEST_CRON = "/schedule?cron="
    GD_HARVEST_CRON = "/schedule"
    G_STATUS = "/status/state"
    G_HEALTH = "/status/health"
    G_PROGRESS = "/status/progress"
    G_MAX_DOCS = "/status/max-documents"
    G_DATA_PROVIDER = "/status/data-provider"
    G_HARVESTED_DOCS = "/status/harvested-documents"
    G_BOOLEAN_OUTDATED_DOCS = "/outdated"

    # HARVESTER_USER = ""
    # HARVESTER_PASS = ""
    # credentials = base64.b64encode(HARVESTER_USER + ':' + HARVESTER_PASS)


class HarvesterApiConstantsV7:
    """

     This Class holds a list of Harvester API constants which will be updated accordingly to the Harvester-BaseLibrary.
     Current version is 7.x.x See: https://wiki.gerdi-project.de/display/GeRDI/Harvester+Library+7.x.x
     
    """
    PG_HARVEST = "/"
    P_HARVEST_ABORT = "/abort"
    P_HARVEST_RESET = "/reset"
    G_HARVEST_LOG = "/log"
    P_HARVEST_CRON = "/schedule/_add" #E.g. {"cronTab" : "0 0 * * *"}
    G_HARVEST_CRON = "/schedule"
    D_HARVEST_CRON = "/schedule/_delete" #E.g. {"cronTab" : "0 0 * * *"}
    DALL_HARVEST_CRON = "/schedule/_deleteAll"
    G_HEALTH = "/health"
    G_BOOLEAN_OUTDATED = "/outdated"

    # HARVESTER_USER = ""
    # HARVESTER_PASS = ""
    # credentials = base64.b64encode(HARVESTER_USER + ':' + HARVESTER_PASS)