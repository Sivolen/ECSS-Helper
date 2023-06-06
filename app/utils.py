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
    create_user_result = client.create_account(user_data=server_data)
    client = EcssHelper(
        api_url=ECSS_API_URL,
        api_port=ECSS_API_PORT,
        ecss_username=USERNAME,
        ecss_password=PASSWORD,
    )
    change_my_from_result = client.change_sip_params(user_data=server_data)
    change_username_result = client.change_displayName(user_data=server_data)
    change_encoding_result = client.change_encoding(user_data=server_data)
    activate_license_result = client.activate_license(user_data=server_data)
    activate_profile_result = client.activate_profile(user_data=server_data)
    return dict(
        create_user_result=create_user_result,
        change_my_from_result=change_my_from_result,
        change_username_result=change_username_result,
        change_encoding_result=change_encoding_result,
        activate_license_result=activate_license_result,
        activate_profile_result=activate_profile_result,
    )


def process(file: list[str]):
    results: dict = {}
    for line in file:
        if len(line) > 0:
            line = line.split(",")
            result = create_sip_user(
                number=line[0].strip(),
                password=line[1].strip(),
                display_name=line[2].strip(),
            )
            results.update(
                {
                    line[0].strip(): dict(
                        creating_status=result["create_user_result"],
                        change_my_from=result["change_my_from_result"],
                        change_name=result["change_username_result"],
                        change_encoding=result["change_encoding_result"],
                        activate_license=result["activate_license_result"],
                        activate_profile=result["activate_profile_result"],
                    )
                }
            )
    return results
