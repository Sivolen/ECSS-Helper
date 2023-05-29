from app.soap import EcssHelper
from settings import (
    USERNAME,
    PASSWORD,
    ECSS_API_URL,
    ECSS_API_PORT,
    DEFAULT_DOMAIN,
    DEFAULT_GROUP,
    DEFAULT_CONTEXT,
    DEFAULT_PROFILE,
    MY_FROM,
    LICENSE_LIST,
    ENCODING,
)


def create_sip_user(
    number,
    password,
    display_name,
):
    server_data = {
        "domain": DEFAULT_DOMAIN,
        "my_from": MY_FROM,  # Need use domain name
        "context": DEFAULT_CONTEXT,
        "group": DEFAULT_GROUP,
        "number": number,
        "password": password,
        "display_name": display_name,
        "encoding": ENCODING,
        "license_list": LICENSE_LIST,
        "profile": DEFAULT_PROFILE,
    }
    client = EcssHelper(
        api_url=ECSS_API_URL,
        api_port=ECSS_API_PORT,
        ecss_username=USERNAME,
        ecss_password=PASSWORD,
    )
    client.create_account(user_data=server_data)
    client = EcssHelper(
        api_url=ECSS_API_URL,
        api_port=ECSS_API_PORT,
        ecss_username=USERNAME,
        ecss_password=PASSWORD,
    )
    client.change_sip_params(user_data=server_data)
    client.change_displayName(user_data=server_data)
    client.change_encoding(user_data=server_data)
    client.activate_license(user_data=server_data)
    client.activate_profile(user_data=server_data)


def process(file):
    with open(file, "r") as f:
        for line in f:
            line = line.split(",")
            create_sip_user(
                number=line[0].strip(),
                password=line[1].strip(),
                display_name=line[2].strip(),
            )
