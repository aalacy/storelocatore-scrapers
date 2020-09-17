import csv
import re
import pdb
import requests
from lxml import etree
import json


base_url = 'https://www.lasenza.com'


def validate(item):    
    if type(item) == list:
        item = ' '.join(item)
    return item.strip()

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
            try:
                writer.writerow(row)
            except:
                pdb.set_trace()

def fetch_data():
    output_list = []
    url = "https://www.lasenza.com/on/demandware.store/Sites-Global-Site/en_US/Stores-GetNearestStores?latitude=43.653226&longitude=-79.38318429999998&countryCode=US&distanceUnit=mi&maxdistance=10000"
    session = requests.Session()
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
        'accept-encoding': 'gzip, deflate, br',
        'cookie': '__cfduid=d8dcdd19e48c9259f5d6b23cc741e2fb11566384436; cqcid=abFPpx5QTucMlpFC3wdKyQ8MZE; wishlistitems={}; guestWishListID=""; dwanonymous_f05b8449cdeb698aa739d69c70fdf52a=abFPpx5QTucMlpFC3wdKyQ8MZE; __cq_dnt=0; dw_dnt=0; dw=1; __zlcmid=ttiThsECEO8eUI; sid=apDm2a5ysqmBCCTx8JKIcDJSsk_udKWZu9o; dwsid=hxnmCZqGSjGvvLCb0biRht_bsp_agF0BlW56-P2MguhB7PtuMBj-JQ7ObOl-w8fFz-AuoRIS6NPlzfF4goUN9A==; dwac_74f0644acfd68de7d2fcfd8762=apDm2a5ysqmBCCTx8JKIcDJSsk_udKWZu9o%3D|dw-only|||CAD|false|US%2FEastern|true; dwsecuretoken_f05b8449cdeb698aa739d69c70fdf52a=FXrVM5C-aHr_RfQkQqvlvb_zLnVVCKEKJg==',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'
    }
    request = session.get(url, headers=headers)
    store_list = json.loads(request.text)['stores']    
    for key, store in list(store_list.items()):
        output = []
        if 'us' in store['countryCode'].lower() or 'ca' in store['countryCode'].lower():
            output.append(base_url) # url
            output.append(get_value(store['name'])) #location name
            output.append(get_value(store['address1'] + ' ' + store['address2'])) #address
            output.append(get_value(store['city'])) #city
            output.append(get_value(store['stateCode'])) #state
            output.append(get_value(store['postalCode'])) #zipcode
            output.append(get_value(store['countryCode']))#country code
            output.append(key) #store_number
            output.append(get_value(store['phone'])) #phone
            output.append("La Senza Store") #location type
            output.append(store['latitude']) #latitude
            output.append(store['longitude']) #longitude
            output.append(get_value(store['storeHours'])) #opening hours
            output_list.append(output)
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
