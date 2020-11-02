import csv
import re
import pdb
import requests
from lxml import etree
import json


base_url = 'https://www.nbarizona.com'


def validate(item):    
    if type(item) == list:
        item = ' '.join(item)
    return item.strip().replace(';', '')

def get_value(item):
    if item == None :
        item = '<MISSING>'
    item = validate(item)
    if item == '':
        item = '<MISSING>'    
    return item

def eliminate_space(items):
    rets = []
    for item in items:
        item = validate(item)
        if item != '':
            rets.append(item)
    return rets

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    output_list = []
    url = "https://www.nbarizona.com/locationservices/searchwithfilter"
    session = requests.Session()
    headers = {
        'accept': '*/*',
        'accept-encoding': 'gzip, deflate, br',
        'content-type': 'application/json',
        'cookie': 'visid_incap_2126369=13Vsb8L/Thu5DIOl6PXEhdG6RF0AAAAAQUIPAAAAAACNu8Y9uBOCUGxeRYC5wF30; plid=5e4c4a6a3007ebfc26788066b87412ec; incap_ses_959_2126369=C1BsDl+9UBuRBD615g1PDZwcXV0AAAAA+ZV2A8AieMWyAp3A3cYTVg==; BIGipServerwww.affiliate.com=!DAOTdtiNz7oNlrWUHXLXyCK7keGtUje/tSgcPS5bD5K0dPEW5el/Qyv578kzzO/Z59q7jS9CPQvXAuU=; lid=e4ae06455eee43e815fec798c784cb83; TS0174630e=0129c692f5938963fe8a71cde39fe2cf306308572bfad601d56379ed35056dee4cbfd310e8c8b6baa9346b18553e367bcf4c1db25e41f284b8a73a9a066de187b7dd3595a2; AMCVS_FFE376A8532209960A490D44%40AdobeOrg=1; s_cc=true; BIGipServerwww.affiliate.com-dp=!gQIpj0G10Xssf/KUHXLXyCK7keGtUjLs6Hr5XuxXnCyiUdw8QLjisszdVtaiq8/9DseUAEMWmBI4Fg==; incap_ses_966_2126369=PVe+dYbpK1X9AhrucxBoDecfX10AAAAAnC/Xc07jCJHUayQTxwRDXQ==; AMCV_FFE376A8532209960A490D44%40AdobeOrg=1687686476%7CMCIDTS%7C18130%7CMCMID%7C23253237222599626351269716577058471698%7CMCAID%7CNONE%7CMCOPTOUT-1566522358s%7CNONE%7CvVersion%7C3.0.0; s_ppn=locations%7C; s_sq=%5B%5BB%5D%5D; s_ppvl=locations%257C%2C38%2C38%2C657%2C949%2C657%2C1366%2C768%2C1%2CP; TS01ee6ffb=0129c692f50dd0cd8438702e3492c34743ad99bfe0ac9a6448ee65ff98d7c66a4b9c4518fd25a0f668159d0fc9106d94bdffd325a990864ca7a88ef1bd2d8be91281e69527f2ec58d0d0df853851c16037e2be334c; s_ppv=locations%257C%2C100%2C38%2C2063%2C1186%2C821%2C1366%2C768%2C0.8%2CP; pp_lastElem=H4:B)%20Bullhead%20City; s_getNewRepeat=1566516283995-Repeat',
        'csrf-token': 'undefined',
        'origin': 'https://www.nbarizona.com',
        'referer': 'https://www.nbarizona.com/locations/',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest'
    }
    data = {
        "channel":"Online",
        "schemaVersion":"1.0",
        "clientUserId":"ZIONPUBLICSITE",
        "clientApplication":"ZIONPUBLICSITE",
        "transactionId":"txId",
        "affiliate":"0116",
        "searchResults":"50000",
        "username":"ZIONPUBLICSITE",
        "searchAddress":{
            "address":"90025",
            "city":"null",
            "stateProvince":"null",
            "postalCode":"null",
            "country":"null"
        },
        "distance":"3000",
        "searchFilters":[{"fieldId":"1","domainId":"116","displayOrder":"1","groupNumber":"1"}]
    }
    request = session.post(url, headers=headers, data=json.dumps(data))
    store_list = json.loads(request.text)['location']    
    for store in store_list:
        output = []
        output.append(base_url) # url
        output.append(get_value(store['locationName'])) #location name
        output.append(get_value(store['address'])) #address
        output.append(get_value(store['city'])) #city
        output.append(get_value(store['stateProvince'])) #state
        output.append(get_value(store['postalCode'])) #zipcode
        output.append(get_value(store['country'])) #country code
        output.append(get_value(store['locationId'])) #store_number
        output.append(get_value(store['phoneNumber'])) #phone
        output.append("National Bank of Arizona") #location type
        output.append(get_value(store['lat'])) #latitude
        output.append(get_value(store['long'])) #longitude
        store_hours = []
        for hour in store['locationAttributes']:
            if 'hours' in hour['name'].lower():
                store_hours.append(get_value(hour['name']) + ' : ' + get_value(hour['value']))
        output.append(', '.join(store_hours)) #opening hours
        output_list.append(output)
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
