import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json


session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    base_url = "https://embassysuites3.hilton.com/en_US/es/ajax/cache/regions.json"
    r = session.get(base_url).json()
    return_main_object = []
    output=[]
    for region in r['region']:
        base_url1 = "https://embassysuites3.hilton.com/en_US/es/ajax/cache/regionHotels.json?regionId="+str(region['id'])+"&subregionId=null&hotelStatus=null"
        r1 = session.get(base_url1).json()
        for hotel in r1['hotels']:
            store = []
            store.append("https://embassysuites3.hilton.com")
            store.append(hotel['name'])
            store.append(hotel['address1'])
            store.append(hotel['city'])
            try:
                store.append(hotel['state'])
            except:
                store.append("<MISSING>")
            try:
                store.append(hotel['zip'].strip())
            except:
                store.append("<MISSING>")
            if hotel['country']=="Canada":
                store.append("CA")
            elif re.search('USA',hotel['country']):
                store.append("US")
            else:
                store.append(hotel['country'])
            store.append("<MISSING>")
            store.append(hotel['phone'])
            store.append("embassysuites3 Hilton")
            store.append(hotel['lat'])
            store.append(hotel['lng'])
            store.append("<MISSING>")
            if hotel['lat'] in output:
                continue
            output.append(hotel['lat'])
            return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
