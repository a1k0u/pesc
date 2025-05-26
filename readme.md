# Pesc-api

Simple python module which provide access to data from [ikus.pesc.ru](https://ikus.pesc.ru/).
Before you use the wrapper you need to register on the [site](https://ikus.pesc.ru/auth/login).

## Authentication

```python
>>> from pesc import PescClient
>>> client = PescClient()
>>> client.auth('sa@prg.re', 'password')
{'authenticationSuccess': True}
```

Also it is possible to authenticate with a phone number.

```python
>>> from pesc import PescClient
>>> client = PescClient()
>>> client.auth('+79001002030', 'password', PescClient.AuthType.PHONE)
{'authenticationSuccess': True}
```

## Accounts

```python
>>> accounts = client.accounts
>>> account = accounts[0]
```

### Bills

```python
>>> bills = account.get_bills(date_from='30.12.2010', date_to='01.01.2016')
>>> bills[0]
{'id': '000000000000000', 'externalId': None, 'accountId': 00000000, 'amount': 0.31, 'timestamp': '01.04.2016 00:00:00', 'file': None, 'canDownload': True}
```

It is possible to download bill file.

```python
>>> account.download_bill(bills[0]["id"], f'bill.pdf')
```

### Payments

```python
>>> payments = account.get_payments(date_from='01.01.2018', date_to='30.05.2018')
>>> payments[0]
{'accountId': 00000000, 'status': 'SUCCESS', 'details': [{'subserviceId': 00000, 'providerServiceId': 000, 'providerServiceName': 'НО "ФКР МКД СПб"', 'fine': {'balance': None, 'accrued': 0.0}, 'charge': {'balance': None, 'accrued': 0000.00}, 'checked': True}], 'timestamp': '2026-04-06T12:00', 'id': '0000000000000', 'file': None, 'receiptUrl': None}
```

## Meters

```python
>>> meters = account.meters
>>> meter = meters[0]
>>> meter.info
[{'id': {'provider': 1100, 'registration': '0000000000'}, 'name': 'Электроэнергия', 'numberOfDigitsLeft': 6, 'numberOfDigitsRight': 0, 'serial': '000000', 'status': 'ACTIVE', 'indications': [{'previousReadingDate': '01.05.2026', 'meterScaleId': 2, 'indicationId': None, 'scaleName': 'День', 'previousReading': 0000.0, 'registerReading': None, 'unit': 'кВт*ч'}, {'previousReadingDate': '01.05.2016', 'meterScaleId': 3, 'indicationId': None, 'scaleName': 'Ночь', 'previousReading': 0000.0, 'registerReading': None, 'unit': 'кВт*ч'}], 'subserviceId': 00000}]
```

### Indications

Get indications

```python
>>> indications = meter.get_indications(date_from='01.01.2018', date_to='30.05.2018')
>>> indications[0]
{'key': '01.05.2016', 'value': [{'key': 00000000, 'value': [{'meterId': {'provider': 1100, 'registration': '00000000000'}, 'period': {'name': '01.05.2016', 'interval': {'dateFrom': '01.05.2016', 'dateTo': '01.05.2016'}, 'deadLine': None}, 'values': [{'scale': 'День', 'value': 0000.0, 'unit': 'кВт*ч', 'consumption': None}, {'scale': 'Ночь', 'value': 0000.0, 'unit': 'кВт*ч', 'consumption': None}], 'source': None}]}]}
```

Post indication

```python
>>> meter.post_indication(day=105, night=10)
True
```

### Logout

```python
>>> client.logout()
{'logoutSuccess': True}
```
