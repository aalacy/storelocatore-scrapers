import csv
import re
import pdb
import requests
from lxml import etree
import json
import usaddress


base_url = 'https://www.thrifty.com'


def validate(item):    
    if item == None:
        item = ''
    if type(item) == int or type(item) == float:
        item = str(item)
    if type(item) == list:
        item = ' '.join(item)
    return item.replace('\u2013', '-').strip()

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

def parse_address(address):
    address = usaddress.parse(address)
    street = ''
    city = ''
    state = ''
    zipcode = ''
    for addr in address:
        if addr[1] == 'PlaceName':
            city += addr[0].replace(',', '') + ' '
        elif addr[1] == 'ZipCode':
            zipcode = addr[0].replace(',', '')
        elif addr[1] == 'StateName':
            state = addr[0].replace(',', '') + ' '
        else:
            street += addr[0].replace(',', '') + ' '
    return { 
        'street': get_value(street), 
        'city' : get_value(city), 
        'state' : get_value(state), 
        'zipcode' : get_value(zipcode)
    }


def fetch_data():
    session = requests.Session()
    history = []
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        url = 'https://www.skiphop.com/on/demandware.store/Sites-Carters-Site/default/Stores-GetNearestStores?postalCode=75201&countryCode=US&distanceUnit=imperial&maxdistance=100000&carters=false&oshkosh=false&skiphop=true&retail=true&wholesale=true'
        page_url = ''
        headers = {
            'accept': 'application/json, text/javascript, */*; q=0.01',
            'cookie': '__cfduid=df4fcaacc5f7a814f66662f4333d819001572299067; dwanonymous_147a2aff3a3cbeff33fff2d813b373d1=abuBCfePHXQXOdjp1nUf1fTmwl; ViewedOptIn=true; a_b_test=test_a; s_fid=26E42E9EDD8FFEC1-156BA157EBD4E56C; dwac_bcWK6iaagGacsaaac72qM7BEZK=XzsiHD0ScPgsAQ869iAmWUsnMO_ehsp6vuU%3D|dw-only|||USD|false|US%2FEastern|true; cqcid=abuBCfePHXQXOdjp1nUf1fTmwl; sid=XzsiHD0ScPgsAQ869iAmWUsnMO_ehsp6vuU; dwsecuretoken_147a2aff3a3cbeff33fff2d813b373d1=Ew_3bryRMzbosdDIqMvpvOD-1XUljLYFDA==; currentSite=skiphop; __cq_dnt=0; dw_dnt=0; dwsid=wGRlSQYOVNo3fb1Ol69d5NR4d7rlmu5YpZklktjFdNNIvPIxLpnj8f-bE-zFfl8qECjGisb0cQgtMXZNiblJ6A==; dw=1; geoCookie=null%7C11.5583%7C104.9121%7CKH; dw_TLSWarning=false; orderconfmodal=talkables; _pxvid=33409549-ffad-11e9-88a2-0242ac120003; _pxff_tm=1; utag_main=v_id:016e1453e682001dbbfdf1841db303073001806b0086e$_sn:2$_ss:0$_st:1572947347083$ses_id:1572945496257%3Bexp-session$_pn:4%3Bexp-session; _px3=76f0038d6effc8f19ea965052d00ab67decd6467cc485a9beebecbfafdac4b21:bZFPOgQwIuatkw4Q47Gd6R2ogc30YiqjblQz1KFdLlImrsKG7Ibq1i379hknlOXv8uTlNfRSEg9kh7wP7YqW/A==:1000:ZwCAxUpbYap040y/VKuOcSIFZzLUBglJz7SYRSr8YHmQcj6RJAL6AeymzyIwA6e8tnL1qnllT8Co53inomQ1+i3z78PV5AJoafSBP8v9YAY4sFJGuRV6AQd5XtxZ0aDxWFZhkyvOKGUM4DvpulBct/xiiXCGUS61+mpTuQ1uQwo=; _px=bZFPOgQwIuatkw4Q47Gd6R2ogc30YiqjblQz1KFdLlImrsKG7Ibq1i379hknlOXv8uTlNfRSEg9kh7wP7YqW/A==:1000:d3w+xa6jhttGi205nssopgvSCtUAHZy7mY4lwpcp+9jZoT5vAlm/qVhfU6kyTEDc8SYIHlqPR3zXuhn6U4jYYm3w9G2hhLYSrPYLaWe6ExXf8ZMTrckH+ct1dREZNQbiO74/kPpjFwIQ459yav8dpGYSdQd/82W6eqW7iergnxfoulqCCbO1H1cNwxg1w+OanI3OvnLcbEniq46BPtiLFJrp+atWNV7dxtTA8S6ge8GtBEERYr7IO8ueV1w5e1P/BPPVV4A9jvj8NBS2IsDZtw==; s_sq=thewilliamcartercartersusdev%3D%2526c.%2526a.%2526activitymap.%2526page%253Dhttps%25253A%25252F%25252Fwww.skiphop.com%25252Ffind-a-store%25253Fid%25253Dskiphop%252526page%25253D1%2526link%253DFIND%252520A%252520STORE%2526region%253Dstoresearchform%2526.activitymap%2526.a%2526.c%2526pid%253Dhttps%25253A%25252F%25252Fwww.skiphop.com%25252Ffind-a-store%25253Fid%25253Dskiphop%252526page%25253D1%2526oid%253DSearch%2526oidt%253D3%2526ot%253DSUBMIT',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.70 Safari/537.36',
            'x-requested-with': 'XMLHttpRequest'
        }
        request = session.get(url, headers=headers)
        store_list = json.loads(request.text)['stores']
        for key, store in list(store_list.items()):
            store_id = get_value(store['storeid'])
            if store_id not in history:
                history.append(store_id)
                output = []
                output.append(base_url) # url
                output.append('https://www.skiphop.com/find-a-store') # page url
                output.append(get_value(store['name'])) #location name
                output.append(get_value(store['address1'] + ', ' + store['address2'])) #address
                output.append(get_value(store['city'])) #city
                output.append(get_value(store['stateCode'])) #state
                output.append(get_value(store['postalCode'])) #zipcode
                output.append(get_value(store['countryCode'])) #country code
                output.append(store_id) #store_number
                output.append(get_value(store['phone'])) #phone
                output.append(get_value(store['brand'])) #location type
                if get_value(store['brand']) == 'skiphop':
                    output.append(get_value(store['latitude'])) #latitude
                    output.append(get_value(store['longitude'])) #longitude
                    store_hours = []
                    days_of_week = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
                    for day in days_of_week:
                        day_key = day + 'Hours'
                        if validate(store[day_key]) != '':
                            store_hours.append(day + ' ' + validate(store[day_key]))
                    output.append(get_value(store_hours)) #opening hours
                    writer.writerow(output)
                    
fetch_data()
