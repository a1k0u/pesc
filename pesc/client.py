# -*- coding: utf-8 -*-
"""
pesc.client

"""

import json
import requests

from datetime import datetime
from enum import Enum

ROOT_URL = "https://ikus.pesc.ru"


class PescObject:
    """
    This is base class.

    """

    def __init__(self, session=requests.Session()):
        self.session = session
        self.session.headers.update(
            {
                "Content-Type": "application/json; charset=utf-8",
            }
        )


class PescMeter(PescObject):
    """
    This class for electric meter.

    """

    def __init__(self, session, account_id, provider_id, meter_id):
        super().__init__(session=session)
        self.account_id = account_id
        self.provider_id = provider_id
        self.api_url = ROOT_URL + "/api"
        self.meter_id = meter_id

    @property
    def info(self):
        return self.session.get(
            f"{self.api_url}/v6/accounts/{self.account_id}/meters/info"
        ).json()

    def get_indications(
        self,
        date_from=datetime.now().strftime("01.01.%Y"),
        date_to=datetime.now().strftime("%d.%m.%Y"),
    ):
        response = self.session.get(
            f"{self.api_url}/v7/reading/individuals",
            params={
                "provider": self.provider_id,
                "account": self.account_id,
                "from": date_from,
                "to": date_to,
            },
        )

        return response.json()

    def post_indication(self, day=0, night=0):
        response = self.session.post(
            f"{self.api_url}/v8/accounts/{self.account_id}/meters/{self.meter_id}/reading",
            json=[
                {"scaleId": 2, "value": day},
                {"scaleId": 3, "value": night},
            ],
        )

        return response.json()

    def __repr__(self):
        return "Meter {} from account {}".format(self.meter_number, self.account_id)


class PescAccount(PescObject):
    """
    This is class for consumer account.

    """

    def __init__(self, session, account_id, provider_id):
        super().__init__(session=session)
        self.api_url = ROOT_URL + "/api"
        self.account_id = account_id
        self.provider_id = provider_id

    def get_bills(
        self,
        date_from=datetime.now().strftime("01.01.%Y"),
        date_to=datetime.now().strftime("%d.%m.%Y"),
    ):
        response = self.session.get(
            f"{self.api_url}/v7/bills/payments",
            params={
                "provider": self.provider_id,
                "account": self.account_id,
                "from": date_from,
                "to": date_to,
            },
        )

        return [
            self.session.get(f"{self.api_url}/v8/payments/bills/{bill_id}").json()
            for bill_id in response.json()
        ]

    def download_bill(self, bill_id, filename):
        uuid = self.session.get(
            f"{self.api_url}/v7/accounts/{self.account_id}/payments/bills/{bill_id}/uuid"
        ).text

        response = self.session.get(f"{self.api_url}/v1/file/{uuid}", stream=True)
        with open(filename, "wb") as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)

    def get_payments(
        self,
        date_from=datetime.now().strftime("01.01.%Y"),
        date_to=datetime.now().strftime("%d.%m.%Y"),
    ):
        response = self.session.get(
            f"{self.api_url}/v7/payments",
            params={
                "provider": self.provider_id,
                "account": self.account_id,
                "from": date_from,
                "to": date_to,
            },
        )

        return [
            self.session.get(f"{self.api_url}/v8/payments/{payment_id}").json()
            for payment_id in response.json()
        ]

    def get_meters(self):
        response = self.session.get(
            f"{self.api_url}/v6/accounts/{self.account_id}/meters/info"
        )

        return [
            PescMeter(
                self.session,
                self.account_id,
                self.provider_id,
                meter["id"]["registration"],
            )
            for meter in response.json()
        ]

    # get_address
    # https://ikus.pesc.ru/api/v8/accounts/.../address

    @property
    def meters(self):
        return self.get_meters()

    @property
    def status(self):
        url = "/".join((self.api_url, self.provider, "status"))
        headers = {"content-type": "application/json; charset=utf-8"}
        data = {"accountNumber": self.account_id, "serviceType": self.service_type}
        response = self.session.post(url, data=json.dumps(data), headers=headers)
        return response.json()

    @property
    def debt(self):
        # https://ikus.pesc.ru/api/v8/accounts/../payments/bills/current ?

        url = "/".join((self.api_url, self.provider, "debt"))
        headers = {"content-type": "application/json; charset=utf-8"}
        data = {"accountNumber": self.account_id, "serviceType": self.service_type}
        response = self.session.post(url, data=json.dumps(data), headers=headers)
        return response.json()

    @property
    def active_payments(self):
        url = "/".join((self.api_url, self.provider, "activePayments"))
        headers = {"content-type": "application/json; charset=utf-8"}
        data = {"accountNumber": self.account_id, "serviceType": self.service_type}
        response = self.session.post(url, data=json.dumps(data), headers=headers)
        return response.json()

    @property
    def address(self):
        # https://ikus.pesc.ru/api/v8/accounts/.../address ?

        url = "/".join((self.api_url, self.provider, "address"))
        headers = {"content-type": "application/json; charset=utf-8"}
        data = {"accountNumber": self.account_id, "serviceType": self.service_type}
        response = self.session.post(url, data=json.dumps(data), headers=headers)
        return response.json()["address"]

    def __repr__(self):
        return "Account {} at {}".format(self.account_id, self.address)


class PescClient(PescObject):
    """
    This is class for access data.

    """

    class AuthType(Enum):
        EMAIL = "EMAIL"
        PHONE = "PHONE"

    def __init__(self):
        super().__init__()
        self.api_url = ROOT_URL + "/api"
        self.login = None
        self.password = None
        self.type = None

    def auth(self, login, password, type=AuthType.EMAIL):
        """
        Authentication function.

        Parameters
        __________
        login: str
            login
        password: str
            password
        type: AuthType
            type of authentication, default is AuthType.EMAIL

        Returns
        _______
        dict
            {'authenticationSuccess': True} or
            {'errors': [{'code': 5, 'message': 'Неавторизованный доступ'}]}
        """
        self.login = login
        self.password = password
        self.type = type

        response = self.session.post(
            f"{self.api_url}/v8/users/auth",
            json={
                "login": login,
                "password": password,
                "type": type.value,
            },
        )

        if response.status_code == 200:
            token = response.json().get("auth")
            self.session.headers.update(
                {
                    "Authorization": f"Bearer {token}",
                }
            )

            return {"authenticationSuccess": True}

        return {
            "errors": [
                {
                    "code": response.status_code,
                    "message": response.json().get("message", "Unknown error"),
                }
            ]
        }

    def check_auth(self):
        """
        Function for checking auth info.

        Returns
        _______
        dict
            {
                'userId': int,
                'name': {
                    'first': str,
                    'last': str,
                    'patronymic': optional[str]
                },
                'fields': List[dict],
                'phone': str,
                'email': str,
                'isConfirmed': bool,
                'isOnBoardingViewed': bool
            }
            or
            {
                'errors': [
                    {'code': 401, 'message': 'Неавторизованный доступ'}
                ]
            }
        """

        response = self.session.get(f"{self.api_url}/v6/users/current")
        if response.status_code != 200:
            return {
                "errors": [
                    {
                        "code": response.status_code,
                        "message": response.json().get("message", "Unknown error"),
                    }
                ]
            }

        return response.json()

    def get_accounts(self):
        """
        Function for getting accounts.

        Returns
        _______
        List[PescAccount]
        """
        response = self.session.get(f"{self.api_url}/v8/accounts")
        if response.status_code != 200:
            return {
                "errors": [
                    {
                        "code": response.status_code,
                        "message": response.json().get("message", "Unknown error"),
                    }
                ]
            }

        return [
            PescAccount(
                self.session,
                account["id"],
                account["service"]["providerId"],
            )
            for account in response.json()
        ]

    @property
    def accounts(self):
        return self.get_accounts()

    @property
    def notifications(self):
        url = self.api_url + "/notifications"
        response = self.session.get(url)
        try:
            notifications = response.json()
        except json.decoder.JSONDecodeError:
            notifications = response.text
        return notifications

    def logout(self):
        """
        Function for logout.

        Return
        ______
        dict
            {'logoutSuccess': True}
        """
        url = self.api_url + "/logout"
        response = self.session.get(url)
        return response.json()
