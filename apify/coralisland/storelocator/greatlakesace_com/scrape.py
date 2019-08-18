import csv
import re
import pdb
import requests
from lxml import etree
import json


base_url = 'https://www.greatlakesace.com'

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    output_list = []
    url = "https://www.greatlakesace.com/locationquery.php?formattedAddress=&boundsNorthEast=&boundsSouthWest="
    session = requests.Session()
    request = session.get(url)
    store_list = json.loads(request.text)
    for store in store_list:
        try:
            output = []
            output.append(base_url) # url
            output.append(store['title']) #location name
            output.append(store['address']) #address
            output.append(store['city']) #city
            output.append(store['state']) #state
            output.append(store['postal']) #zipcode
            output.append('US') #country code
            output.append('<MISSING>') #store_number
            output.append(store['phone'] if store['phone'] != 'N/A' else '<MISSING>') #phone
            output.append('Great Lakes Ace Stores') #location type
            output.append(store['lat']) #latitude
            output.append(store['lng']) #longitude        
            h_temp = store['hours1'] + ', ' + store['hours2'] + ', ' + store['hours3']
            output.append(h_temp) #opening hours
            output_list.append(output)
        except:
            pass
    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
