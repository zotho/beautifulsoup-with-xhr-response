# https://stackoverflow.com/questions/56579958/scraping-data-from-a-xhr-with-request

import requests
from bs4 import BeautifulSoup
import re
import json
import pandas as pd

# Let's first collect few auth vars
r = requests.Session()
response = r.get(
    "https://simuladores.bancosantander.es/SantanderES/loansimulatorweb.aspx?por=webpublica&prv=publico&m=100&cta=1"
    "&ls=0#/t0")
soup = BeautifulSoup(response.content, 'html.parser')
key = soup.find_all('script', text=re.compile('Afi.AfiAuth.Init'))
pattern = r"Afi.AfiAuth.Init\((.*?)\)"

WSSignature = re.findall(pattern, key[0].text)[0].split(',')[-1].replace('\'', '')
WSDateTime = re.findall(pattern, key[0].text)[0].split(',')[1].replace('\'', '')

headers = {
    'Origin': 'https://simuladores.bancosantander.es',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/74.0.3729.169 Safari/537.36',
    'Content-Type': 'application/json;charset=UTF-8',
    'Accept': 'application/json, text/plain, */*',
    'WSSignature': WSSignature,
    'Referer': 'https://simuladores.bancosantander.es/SantanderES/loansimulatorweb.aspx?por=webpublica&prv=publico&m'
               '=100&cta=1&ls=0',
    'WSDateTime': WSDateTime,
    'WSClientCode': 'SantanderES',
}

# Those are the standard params of a request
params = {'wsInputs': {'finality': 'prestamo coche',
                       'productCode': 'p100',
                       'capitalOrInstallment': 5000,
                       'monthsTerm': 96,
                       'mothsInitialTerm': 12,
                       'openingCommission': 1.5,
                       'minOpeningCommission': 60,
                       'financeOpeningCommission': True,
                       'interestRate': 5.5,
                       'interestRateReferenceIndex': 0,
                       'interestRateSecondaryReferenceIndex': 0,
                       'interestRateSecondaryWithoutVinculation': 6.5,
                       'interestRateSecondaryWithAllVinculation': 0,
                       'interestRateSecondary': 6.5,
                       'loanDate': '2019-06-13',
                       'birthDate': '2001-06-13',
                       'financeLoanProtectionInsurance': True,
                       'percentageNotaryCosts': 0.003,
                       'loanCalculationMethod': 0,
                       'calculationBase': 4,
                       'frecuencyAmortization': 12,
                       'frecuencyInterestPay': 12,
                       'calendarConvention': 0,
                       'taeCalculationBaseType': 4,
                       'lackMode': 0,
                       'amortizationCarencyMonths': 0,
                       'typeAmortization': 1,
                       'insuranceCostSinglePremium': 0,
                       'with123': False,
                       'electricVehicle': False}}


# The scraping function
def scrap(in_amount, in_duration, in_params):
    in_params['wsInputs']['capitalOrInstallment'] = in_amount
    in_params['wsInputs']['monthsTerm'] = in_duration
    scrap_response = r.post(
        'https://simuladores.bancosantander.es/WS/WSSantanderTotalLoan.asmx/Calculate',
        headers=headers,
        data=json.dumps(in_params)
    )
    return json.loads(scrap_response.content)['d']


Amounts = [13000]
Durations = [48, 60, 72, 84, 96]
results = []
for amount in Amounts:
    for duration in Durations:
        result = scrap(amount, duration, params)
        result['Amount'] = amount
        result['Duration'] = duration
        results.append(result)

df = pd.DataFrame(results)
print(df)
