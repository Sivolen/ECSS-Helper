#!venv/bin/python3
import re

import requests
from requests.cookies import cookiejar_from_dict

# from xmlschema import XMLSchema
from urllib3 import exceptions, disable_warnings

# import xml.etree.ElementTree as ET
import xmltodict

from settings import USERNAME, PASSWORD, ECSS_API_URL, ECSS_API_PORT

disable_warnings(exceptions.InsecureRequestWarning)


# API_LOGIN_XML = '<in><login user = "" password=" /></in>'


# url_login = 'https://10.40.1.23:9999/system/login'
# response = requests.post(url_login, data=API_LOGIN_XML, auth=(login, password), verify=False)
# token = response.cookies["token"]
# print(token)
# HEADERS = {'Authorization': f"Cookie token={token}", 'content-type': 'text/xml'}
# cookies = {"token": token}


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
        return True if self.pusher.get(URL).status_code == 200 else False

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
    def check_display_name(display_name: str) -> bool:
        pattern: str = r"^\D{,7}\s\D{,10}\s[A-Z]\.[A-Z]\.$"
        return False if not re.findall(pattern, display_name) else True

    @staticmethod
    def check_number(numbers: str) -> bool:
        pattern: str = r"^[236][0-9]{4}$"
        return False if not re.findall(pattern, numbers) else True

    def __post_data(self, url: str, request: str):
        if not self.__get_connection():
            self.__reconnect()
        data = self.pusher.post(url, request)
        print(data)
        return data

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
        return True if response.status_code == 201 else False

    def create_account(self, user_data: dict[str, str | int | list[str]]) -> bool:
        if not self.check_number(user_data.get("number")):
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
        return False if response.status_code != 206 else True

    def process(
        self, username: str, password: str, user_data: dict, api_url: str, api_port: int
    ) -> None:
        pass

    def change_displayName(self, user_data: dict[str, str | int | list[str]]):
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
        self.__post_data(url=URL_ALIAS, request=XML_ALIAS)

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
        self.__post_data(url=URL_IFACE, request=XML_ENCODING)

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

    def activate_license(self, user_data: dict[str, str | int | list[str]]):
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
            self.__post_data(url=URL_SS, request=XML_SS)

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
        self.__post_data(url=URL_PROFILE, request=XML_PROFILE)


def get_requests(
    ecss_username: str, ecss_password: str, api_url: str, api_port: int
) -> requests:
    URL_LOGIN: str = f"https://{api_url}:{api_port}/system/login"
    XML_API_LOGIN: str = (
        f'<in><login user = "{ecss_username}" password="{ecss_password}" /></in>'
    )
    response = requests.post(
        URL_LOGIN, data=XML_API_LOGIN, auth=(ecss_username, ecss_password), verify=False
    )
    cookies = {"token": response.cookies["token"]}
    r = requests.session()
    r.cookies = cookiejar_from_dict(cookies)
    r.verify = False
    r.timeout = 3
    return r


def post_data(url: str, request: str, poster: requests):
    data = poster.post(url, request)
    print(data)
    return data.content


# def get_iface_id_old(iface_name: str, cookies: dict) -> str:
#     url_iface_info = 'https://10.40.1.23:9999/commands/iface_list'
#     iface_info = '<?xml version="1.0" encoding="UTF-8"?>' \
#                  '<in xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" ' \
#                  'xsi:noNamespaceSchemaLocation="hc_iface_list.xsd">' \
#                  '<request domain="ecss.rt.local"/></in>'
#     response1 = requests.post(url_iface_info, data=iface_info, headers=HEADERS, cookies=cookies, verify=False)
#     my_dict = xmltodict.parse(response1.content)["out"]['ifaces']['iface']
#     iface_id = [i["@id"] for i in my_dict if i['@name'] == iface_name][0]
#     return iface_id


def get_iface_id(
    group: str, number: str, domain: str, poster: requests, api_url: str, api_port: int
) -> str:
    URL_USER: str = f"https://{api_url}:{api_port}/commands/sip_user_show"
    XML_USER_INFO: str = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        "<in "
        'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="sip_user_show.xsd">'
        f'<sip group="{group}" id="{number}@{domain}" domain="{domain}" complete="true"/>'
        "</in>"
    )
    data = post_data(url=URL_USER, request=XML_USER_INFO, poster=poster)
    return xmltodict.parse(data)["out"]["users"]["user"]["@id"]


def create_account(poster: requests, user_data: dict, api_url: str, api_port: int):
    URL_DECLARE: str = f"https://{api_url}:{api_port}/commands/sip_user_declare"
    XML_CREATE_USER: str = (
        f'<in xmlns:xs="http://www.w3.org/2001/XMLSchema-instance">'
        "<request "
        f'domain="{user_data.get("domain")}" '
        f'context="{user_data.get("contex")}" '
        f'group="{user_data.get("group")}" '
        f'iface="{user_data.get("number")}@{user_data.get("domain")}" '
        f'address="alias-as-user" '
        f'auth_qop="no" '
        f'login="{user_data.get("number")}" '
        f'password="{user_data.get("password")}"/>'
        "</in>"
    )
    post_data(url=URL_DECLARE, request=XML_CREATE_USER, poster=poster)


def change_displayName(poster: requests, user_data: dict, api_url: str, api_port: int):
    URL_ALIAS: str = f"https://{api_url}:{api_port}/commands/alias_set"
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
    post_data(url=URL_ALIAS, request=XML_ALIAS, poster=poster)


def change_encoding(poster: requests, user_data: dict, api_url: str, api_port: int):
    URL_IFACE: str = f"https://{api_url}:{api_port}/commands/iface_user_set"
    XML_ENCODING: str = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<in xmlns:xs="http://www.w3.org/2001/XMLSchema-instance" xs:noNamespaceSchemaLocation="iface_user_set.xsd">'
        f'<request owner="sip1" '
        f'domain="{user_data.get("domain")}" '
        f'group="{user_data.get("group")}" '
        f'ifaces="{user_data["iface_id"]}" '
        f'support_encoding="utf8"/>'
        "</in>"
    )
    f"""
        <?xml version="1.0" encoding="UTF-8"?>
        <in xmlns:xs="http://www.w3.org/2001/XMLSchema-instance" xs:noNamespaceSchemaLocation="iface_user_set.xsd">
        <request owner="sip1" 
        domain="{user_data.get("domain")}" 
        group="{user_data.get("group")}" 
        ifaces="{user_data["iface_id"]}" 
        support_encoding="utf8"/>
        </in>
    """
    post_data(url=URL_IFACE, request=XML_ENCODING, poster=poster)


def activate_license(poster: requests, user_data: dict, api_url: str, api_port: int):
    URL_SS: str = f"https://{api_url}:{api_port}/commands/ss_licence_package_allocate"
    license_list: list = [
        "ECSS-ADV",
        "ECSS-ADV+",
        "ECSS-BAS",
        "ECSS-BAS+",
        "ECSS-GEN",
    ]
    for ecss_license in license_list:
        XML_SS: str = f"""
                    <in xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" 
                        xsi:noNamespaceSchemaLocation="hc_ss_licence_package_allocate.xsd"> 
                        <request domain="{user_data["domain"]}" 
                        addresses="{user_data["number"]}" 
                        package="{ecss_license}"/> 
                    </in>
                """
        post_data(url=URL_SS, request=XML_SS, poster=poster)


def activate_profile(poster: requests, user_data: dict, api_url: str, api_port: int):
    URL_PROFILE: str = (
        f"https://{api_url}:{api_port}/commands/ss_domain_profile_activate"
    )
    XML_PROFILE: str = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<in xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
        'xsi:noNamespaceSchemaLocation="hc_ss_domain_profile_activate.xsd">'
        f'<request domain="{user_data["domain"]}">'
        f'<activate profile="phone_profile_01" address="{user_data["number"]}">'
        "</activate>"
        "</request>"
        "</in>"
    )
    post_data(url=URL_PROFILE, request=XML_PROFILE, poster=poster)


def process(
    username: str, password: str, user_data: dict, api_url: str, api_port: int
) -> None:
    # init poster
    poster = get_requests(
        ecss_username=username,
        ecss_password=password,
        api_url=api_url,
        api_port=api_port,
    )

    # Create sip account
    create_account(poster, user_data, api_url=api_url, api_port=api_port)

    # init poster
    poster = get_requests(
        ecss_username=username,
        ecss_password=password,
        api_url=api_url,
        api_port=api_port,
    )

    # add displayname
    change_displayName(
        poster=poster, user_data=user_data, api_url=api_url, api_port=api_port
    )
    iface_id = get_iface_id(
        poster=poster,
        number=user_data["number"],
        domain=user_data["domain"],
        group=user_data["group"],
        api_url=api_url,
        api_port=api_port,
    )
    user_data.update({"iface_id": iface_id})

    # enable support encoding "utf8"
    change_encoding(
        poster=poster, user_data=user_data, api_url=api_url, api_port=api_port
    )

    # activate sip license
    activate_license(
        poster=poster, user_data=user_data, api_url=api_url, api_port=api_port
    )

    # Activation of additional services
    activate_profile(
        poster=poster, user_data=user_data, api_url=api_url, api_port=api_port
    )


def main():
    test_data = {
        "domain": "ecss.rt.local",
        "context": "test_name",
        "group": "123333",
        "number": "32247",
        "password": "7844247",
        "display_name": "GKUCDM Suslov V.G.",
        "encoding": "utf8",
        "license_list": [
            "ECSS-ADV",
            "ECSS-ADV+",
            "ECSS-BAS",
            "ECSS-BAS+",
            "ECSS-GEN",
        ],
    }
    process(
        username=USERNAME,
        password=PASSWORD,
        user_data=test_data,
        api_url=ECSS_API_URL,
        api_port=ECSS_API_PORT,
    )


def main1():
    with open("users.txt", "r") as f:
        for line in f:
            line = line.split(",")
            test_data = {
                "domain": "ecss.rt.local",
                "my_from": "10.40.1.23",  # Need use domain name
                "context": "test_name",
                "group": "123333",
                "number": f"{line[0].strip()}",
                "password": f"{line[1].strip()}",
                "display_name": f"{line[2].strip()}",
                "encoding": "utf8",
                "license_list": [
                    "ECSS-ADV",
                    "ECSS-ADV+",
                    "ECSS-BAS",
                    "ECSS-BAS+",
                    "ECSS-GEN",
                ],
                "profile": "phone_profile_01",
            }
            print(test_data)
            client = EcssHelper(
                api_url=ECSS_API_URL,
                api_port=ECSS_API_PORT,
                ecss_username=USERNAME,
                ecss_password=PASSWORD,
            )
            print(client.create_account(user_data=test_data))
            client = EcssHelper(
                api_url=ECSS_API_URL,
                api_port=ECSS_API_PORT,
                ecss_username=USERNAME,
                ecss_password=PASSWORD,
            )
            client.change_sip_params(user_data=test_data)
            client.change_displayName(user_data=test_data)
            client.change_encoding(user_data=test_data)
            client.activate_license(user_data=test_data)
            client.activate_profile(user_data=test_data)


if __name__ == "__main__":
    main1()
