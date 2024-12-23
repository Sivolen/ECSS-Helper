#!venv/bin/python3
import re
import requests
from requests.cookies import cookiejar_from_dict

from urllib3 import exceptions, disable_warnings

import xmltodict

from settings import STATUS_CODES

disable_warnings(exceptions.InsecureRequestWarning)


class EcssHelper:
    """
    This class can create a user sip on Eltex PBX and preconfigure it,
    activate licenses and add a service profile
    """

    disable_warnings(exceptions.InsecureRequestWarning)

    def __init__(
        self,
        api_url: str,
        api_port: int,
        ecss_username: str,
        ecss_password: str,
    ):
        self.api_url: str = api_url
        self.api_port: int = api_port
        self.ecss_username: str = ecss_username
        self.ecss_password: str = ecss_password
        URL_LOGIN: str = f"https://{self.api_url}:{self.api_port}/system/login"
        XML_API_LOGIN: str = f'<in><login user = "{self.ecss_username}" password="{self.ecss_password}" /></in>'
        HEADERS = {"Content-Type": "text/xml"}
        self.response = requests.post(
            URL_LOGIN,
            data=XML_API_LOGIN,
            headers=HEADERS,
            auth=(self.ecss_username, self.ecss_password),
            verify=False,
        )

        self.cookies = {"token": self.response.cookies["token"]}
        self.pusher = requests.session()
        self.pusher.cookies = cookiejar_from_dict(self.cookies)
        self.pusher.headers = HEADERS
        self.pusher.verify = False
        self.pusher.timeout = 3

    def __get_connection(self):
        """check connection to sip server"""
        URL = f"https://{self.api_url}:{self.api_port}/system/is_active"
        try:
            return True if self.pusher.get(URL).status_code == 200 else False
        except:
            return False

    def __reconnect(self):
        """
        If session is closed, reconnect
        :return:
        """
        URL_LOGIN: str = f"https://{self.api_url}:{self.api_port}/system/login"
        XML_API_LOGIN: str = f'<in><login user = "{self.ecss_username}" password="{self.ecss_password}" /></in>'
        HEADERS = {"Content-Type": "text/xml"}
        self.response = requests.post(
            URL_LOGIN,
            data=XML_API_LOGIN,
            headers=HEADERS,
            auth=(self.ecss_username, self.ecss_password),
            verify=False,
        )

        self.cookies = {"token": self.response.cookies["token"]}
        self.pusher = requests.session()
        self.pusher.cookies = cookiejar_from_dict(self.cookies)
        self.pusher.headers = HEADERS
        self.pusher.verify = False
        self.pusher.timeout = 3

    @staticmethod
    def __check_password_security(password: str) -> bool:
        pattern = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%_])[a-zA-Z\d!@#$%^&*()_+}{:?><]{8,}$"
        return True if re.findall(pattern, password) else False

    @staticmethod
    def __check_display_name(display_name: str) -> bool:
        pattern: str = r"^\D{,7}\s\D{,10}\s[A-ZА-ЯЁ]\.[A-ZА-ЯЁ]\.$"
        return False if not re.findall(pattern, display_name) else True

    @staticmethod
    def __check_number(numbers: str) -> bool:
        pattern: str = r"^[1236][0-9]{4}$"
        return False if not re.findall(pattern, numbers) else True

    def __post_data(self, url: str, request: str):
        if not self.__get_connection():
            self.__reconnect()
        try:
            data = self.pusher.post(url, request.encode("utf-8"))
            return data
        except Exception as send_api_error:
            print(send_api_error)
            return 404

    def change_sip_params(self, user_data: dict[str, str | int | list[str]]):
        URL_SIP_SET: str = (
            f"https://{self.api_url}:{self.api_port}/commands/sip_user_set"
        )
        XML_SIP_SET: str = (
            '<?xml version="1.0" encoding="UTF-8"?>'
            '<in xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
            'xsi:noNamespaceSchemaLocation="sip_user_set.xsd">'
            f'<sip group="{user_data.get("group")}" '
            f'id="{user_data.get("number")}@{user_data.get("domain")}" '
            f'domain="{user_data.get("domain")}">'
            f'<my_from value="{user_data.get("my_from")}"/>'
            "</sip>"
            "</in>"
        )
        response = self.__post_data(url=URL_SIP_SET, request=XML_SIP_SET)
        return True if response.status_code in STATUS_CODES else False

    def create_account(self, user_data: dict[str, str | int | list[str]]) -> bool:
        if not self.__check_number(user_data.get("number")):
            return False
        if not self.__check_password_security(user_data.get("password")):
            return False
        URL_DECLARE: str = (
            f"https://{self.api_url}:{self.api_port}/commands/sip_user_declare"
        )
        XML_CREATE_USER: str = (
            f'<in xmlns:xs="http://www.w3.org/2001/XMLSchema-instance">'
            "<request "
            f'domain="{user_data.get("domain")}" '
            f'context="{user_data.get("context")}" '
            f'group="{user_data.get("group")}" '
            f'iface="{user_data.get("number")}@{user_data.get("domain")}" '
            f'address="alias-as-user" '
            f'auth_qop="no" '
            f'login="{user_data.get("number")}" '
            f'password="{user_data.get("password")}"/>'
            "</in>"
        )
        response = self.__post_data(url=URL_DECLARE, request=XML_CREATE_USER)
        return False if response.status_code not in STATUS_CODES else True

    def process(
        self, username: str, password: str, user_data: dict, api_url: str, api_port: int
    ) -> None:
        pass

    def change_displayName(self, user_data: dict[str, str | int | list[str]]):
        if not self.__check_display_name(user_data.get("display_name")):
            return False
        URL_ALIAS: str = f"https://{self.api_url}:{self.api_port}/commands/alias_set"
        XML_ALIAS: str = (
            '<?xml version="1.0" encoding="UTF-8"?>'
            '<in xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
            'xsi:noNamespaceSchemaLocation="set_alias_properties.xsd">'
            f'<aliases addr="{user_data.get("number")}" '
            f'iface="{user_data.get("number")}@{user_data.get("domain")}" '
            f'domain="{user_data.get("domain")}">'
            f'<property name="displayName" value="{user_data["display_name"]}"/>'
            "</aliases>"
            "</in>"
        )
        response = self.__post_data(url=URL_ALIAS, request=XML_ALIAS)
        return True if response.status_code in STATUS_CODES else False

    def change_encoding(self, user_data: dict[str, str | int | list[str]]):
        URL_IFACE: str = (
            f"https://{self.api_url}:{self.api_port}/commands/iface_user_set"
        )
        XML_ENCODING: str = (
            '<?xml version="1.0" encoding="UTF-8"?>'
            '<in xmlns:xs="http://www.w3.org/2001/XMLSchema-instance" '
            'xs:noNamespaceSchemaLocation="iface_user_set.xsd">'
            f'<request owner="sip1" '
            f'domain="{user_data.get("domain")}" '
            f'group="{user_data.get("group")}" '
            f'ifaces="{self.__get_iface_id(user_data=user_data)}" '
            f'support_encoding="{user_data["encoding"]}"/>'
            "</in>"
        )
        f"""
            <?xml version="1.0" encoding="UTF-8"?>
            <in xmlns:xs="http://www.w3.org/2001/XMLSchema-instance" 
            xs:noNamespaceSchemaLocation="iface_user_set.xsd">
            <request owner="sip1" 
            domain="{user_data.get("domain")}" 
            group="{user_data.get("group")}" 
            ifaces="{self.__get_iface_id(user_data=user_data)}" 
            support_encoding="{user_data["encoding"]}"/>
            </in>
        """
        response = self.__post_data(url=URL_IFACE, request=XML_ENCODING)
        return True if response.status_code in STATUS_CODES else False

    def __get_iface_id(self, user_data: dict[str, str | int | list[str]]) -> str | None:
        URL_USER: str = f"https://{self.api_url}:{self.api_port}/commands/sip_user_show"
        XML_USER_INFO: str = (
            '<?xml version="1.0" encoding="UTF-8"?>'
            "<in "
            'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="sip_user_show.xsd">'
            f'<sip group="{user_data.get("group")}" '
            f'id="{user_data.get("number")}@{user_data.get("domain")}" '
            f'domain="{user_data.get("domain")}" complete="true"/>'
            "</in>"
        )
        data = self.__post_data(url=URL_USER, request=XML_USER_INFO)
        if not data.status_code == 200:
            return
        return xmltodict.parse(data.content)["out"]["users"]["user"]["@id"]

    def activate_license(
        self, user_data: dict[str, str | int | list[str]]
    ) -> dict[str, str]:
        activate_dict: dict = {}
        URL_SS: str = f"https://{self.api_url}:{self.api_port}/commands/ss_licence_package_allocate"
        for ecss_license in user_data["license_list"]:
            XML_SS: str = f"""
                        <in xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" 
                            xsi:noNamespaceSchemaLocation="hc_ss_licence_package_allocate.xsd"> 
                            <request domain="{user_data["domain"]}" 
                            addresses="{user_data["number"]}" 
                            package="{ecss_license}"/> 
                        </in>
                    """
            response = self.__post_data(url=URL_SS, request=XML_SS)
            result = True if response.status_code in STATUS_CODES else False
            activate_dict.update({ecss_license: result})
        return activate_dict

    def activate_profile(self, user_data: dict[str, str | int | list[str]]):
        URL_PROFILE: str = f"https://{self.api_url}:{self.api_port}/commands/ss_domain_profile_activate"
        XML_PROFILE: str = (
            '<?xml version="1.0" encoding="UTF-8"?>'
            '<in xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
            'xsi:noNamespaceSchemaLocation="hc_ss_domain_profile_activate.xsd">'
            f'<request domain="{user_data["domain"]}">'
            f'<activate profile="{user_data["profile"]}" address="{user_data["number"]}">'
            "</activate>"
            "</request>"
            "</in>"
        )
        response = self.__post_data(url=URL_PROFILE, request=XML_PROFILE)
        return True if response.status_code in STATUS_CODES else False
