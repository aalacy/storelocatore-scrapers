import csv
import re
import pdb
import requests
from lxml import etree
import json
import usaddress


base_url = 'https://www.chevrolet.com'


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
    output_list = []
    history = []
    with open('./cities.json') as data_file:    
        city_list = json.load(data_file)  
    page_url = 'https://www.chevrolet.com/dealer-locator'
    headers = {
        'accept': 'application/json, text/plain, */*',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.9',
        'clientapplicationid': 'OCNATIVEAPP',
        'cookie': 'LPVID=Q4MDBlYWFiYzRhNGJkYTk0; GMWP_location=country_code=IE,region_code=,city=DUBLIN,county=,zip=; LPSID-65948500=dLaSIJbBR66oOtFdD3PEyg',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36'
    }
    session = requests.Session()
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for city in city_list:
            url = "https://www.chevrolet.com/OCRestServices/dealer/latlong/v1/chevrolet/"+str(city['latitude'])+"/"+str(city['longitude'])+"/?distance=500&filterByType=services&maxResults=25"
            request = session.get(url, headers=headers)
            data = json.loads(request.text)
            if 'payload' in data:
                store_list = data['payload']['dealers']
                for store in store_list:
                    store_id = get_value(store['id'])
                    if store_id not in history:
                        history.append(store_id)
                        output = []
                        output.append(base_url) # url
                        output.append(page_url) # page url
                        output.append(get_value(store['dealerName'])) #location name
                        output.append(get_value(store['address']['addressLine1'])) #address
                        output.append(get_value(store['address']['cityName'])) #city
                        output.append(get_value(store['address']['countrySubdivisionCode'])) #state
                        output.append(get_value(store['address']['postalCode'])) #zipcode
                        output.append(get_value(store['address']['countryIso'])) #country code
                        output.append(store_id) #store_number
                        output.append(get_value(store['generalContact']['phone1'])) #phone
                        output.append('Chevy Car Dealerships') #location type
                        output.append(get_value(store['geolocation']['latitude'])) #latitude
                        output.append(get_value(store['geolocation']['longitude'])) #longitude
                        days_of_week = ['','Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                        hours = store['generalOpeningHour']
                        store_hours = []
                        for hour in hours:
                            for day in hour['dayOfWeek']:
                                store_hours.append(days_of_week[day] + ' ' + hour['openFrom'] + ' - ' + hour['openTo'])
                        output.append(get_value(store_hours)) #opening hours            
                        writer.writerow(output)                        

fetch_data()