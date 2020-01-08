"""
This Module holds constant classes
"""
# import base64

__author__ = "Jan Frömberg, Laura Höhle"
__copyright__ = "Copyright 2018, GeRDI Project"
__credits__ = ["Jan Frömberg"]
__license__ = "Apache 2.0"
__maintainer__ = "Jan Frömberg"
__email__ = "jan.froemberg@tu-dresden.de"


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
    REPO_NAME = "repositoryName"
    MAX_DOCUMENTS = "max_docs"
    HARVESTED_COUNT = "harvestedCount"
    MAX_DOCUMENT_COUNT = "maxDocumentCount"
    PROGRESS = "progress"
    PROGRESS_MAX = "progress_max"
    # progress current in percentage
    PROGRESS_CURRENT = "progress_cur"
    # in millisecs
    REMAIN_HARVEST_TIME = "remainingHarvestTime"
    LAST_HARVEST_DATE = "lastHarvestDate"
    NEXT_HARVEST_DATE = "nextHarvestDate"
    CRONTAB = "cron"
    POSTCRONTAB = "cronTab"
    NO_CRONTAB = "no crontab defined yet"
    NO_LOGTEXT = "no log"
    SCHEDULE = "scheduledHarvestTasks"
    LOGS = "log"
    LOG_DATA = "log_data"

    OK = "OK"
    N_A = "N/A"
    MESSAGE = "message"

    INIT = "initialization"
    HARV = "harvesting"
    IDLE = "idle"
    IDLE_OLD = "ideling"
    HARVESTER_STATES = [INIT, HARV, IDLE, IDLE_OLD]

    WARNING = "warning"
    SUCCESS = "success"
    PRIMARY = "primary"
    INFO = "info"

    SESSION_KEYS = [
        "theme",
        "viewtype",
        "toolbox",
        "chart",
        "enabled_harvs",
        "disabled_harvs"]


class HarvesterApiConstants:
    """

     This Class holds a list of Harvester Library API constants
     which will be updated accordingly to the Harvester-BaseLibrary.

    """
    G_VERSIONS = "/versions"


class HarvesterApiConstantsV6:
    """

     This Class holds a list of Harvester Library API constants
     which will be updated accordingly to the Harvester-BaseLibrary.

    """
    PRETTY_FLAG = "?pretty"
    P_HARVEST = "/"
    P_HARVEST_ABORT = "/abort"
    P_HARVEST_RESET = "/reset"
    G_HARVEST_LOG = "/log?date="
    HARVESTER_LOG_FORMAT = "%Y-%m-%d"
    G_HARVEST_ALLLOG = "/log"
    P_HARVEST_SUBMIT = "/submit"
    P_HARVEST_SAVE = "/save"
    PD_HARVEST_CRON = "/schedule?cron="
    GD_HARVEST_CRON = "/schedule"
    G_STATUS = "/status/state"
    G_HEALTH = "/status/health"
    # progress: N/A or 123/456
    G_PROGRESS = "/status/progress"
    G_MAX_DOCS = "/status/max-documents"
    G_DATA_PROVIDER = "/status/data-provider"
    G_HARVESTED_DOCS = "/status/harvested-documents"
    G_BOOLEAN_OUTDATED_DOCS = "/outdated"
    G_HARVEST_CONFIG = "/config"
    P_HARVEST_CONFIG = "/config/_set"

    HARVESTER_USER = ""
    HARVESTER_PASS = ""
    # CREDENTIALS = base64.b64encode(HARVESTER_USER + ':' + HARVESTER_PASS)


class HarvesterApiConstantsV7:
    """

     This Class holds a list of Harvester API constants
     which will be updated accordingly to the Harvester-BaseLibrary.
     Current version is 7.x.x See:
     https://wiki.gerdi-project.de/display/GeRDI/Harvester+Library+7.x.x

    """
    PRETTY_FLAG = "?pretty"
    PG_HARVEST = "/"
    P_HARVEST_ABORT = "/abort"
    P_HARVEST_RESET = "/reset"
    G_HARVEST_LOG = "/log?date="
    HARVESTER_LOG_FORMAT = "%Y-%m-%d"
    G_HARVEST_ALLLOG = "/log"
    P_HARVEST_CRON = "/schedule/_add"  # E.g. {"cronTab" : "0 0 * * *"}
    G_HARVEST_CRON = "/schedule"
    D_HARVEST_CRON = "/schedule/_delete"  # E.g. {"cronTab" : "0 0 * * *"}
    DALL_HARVEST_CRON = "/schedule/_deleteAll"
    G_HEALTH = "/health"
    G_BOOLEAN_OUTDATED = "/outdated"
    G_HARVEST_CONFIG = "/config"
    P_HARVEST_CONFIG = "/config/_set"
    STATE_HISTORY = "/etls"

    HARVESTER_USER = ""
    HARVESTER_PASS = ""
    # CREDENTIALS = base64.b64encode(HARVESTER_USER + ':' + HARVESTER_PASS)
