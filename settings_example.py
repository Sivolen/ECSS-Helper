USERNAME: str = ""
PASSWORD: str = ""
ECSS_API_URL: str = "ecss.local"
ECSS_API_PORT: int = 9999
STATUS_CODES: tuple = (
    200,
    201,
    202,
    204,
    203,
    205,
    206,
    207,
    208,
)
LICENSE_LIST: tuple = (
    "ECSS-ADV",
    "ECSS-ADV+",
    "ECSS-BAS",
    "ECSS-BAS",
    "ECSS-BAS+",
    "ECSS-GEN",
)
DEFAULT_DOMAIN: str = "ecss.local"
DEFAULT_CONTEXT: str = ""
DEFAULT_GROUP: str = ""
DEFAULT_PROFILE: str = ""
CHANGE_MY_FROM: bool = False
MY_FROM: str = ""
ENCODING: str = "utf8"
# Login LDAP
AD_ADDRESS: str = "10.0.0.1"
AD_SEARCH_TREE: str = "DC=LOCAL"
#
SLEEP_TIMER: int = 1
