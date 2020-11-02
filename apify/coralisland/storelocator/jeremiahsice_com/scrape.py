import csv
import re
import pdb
import requests
from lxml import etree
import json


base_url = 'https://jeremiahsice.com'

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    output_list = []
    url = "https://jeremiahsice.com/locationlist"
    session = requests.Session()
    request = session.get(url)
    store_list = json.loads(request.text)
    for key, store in list(store_list.items()):
        output = []
        output.append(base_url) # url
        output.append( store['title']) #location name
        output.append(store['street']) #address
        output.append(store['city']) #city
        output.append(store['state']) #state
        output.append(store['zip']) #zipcode
        output.append('US') #country code
        output.append('<MISSING>') #store_number
        output.append(store['phone']) #phone
        output.append("JEREMIAH'S ITALIAN ICE") #location type
        output.append(store['lat']) #latitude
        output.append(store['lng']) #longitude
        if  store['summer_weekday_hour_open']:
            store_hours = 'SU-TH:' + store['summer_weekday_hour_open'].upper() + '-' + store['summer_weekday_hour_close'].upper() + ', '
            store_hours += 'FR-SA:' + store['summer_weekend_hour_open'].upper() + '-' + store['summer_weekend_hour_close'].upper()
            output.append(store_hours) #opening hours        
            output_list.append(output)
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
