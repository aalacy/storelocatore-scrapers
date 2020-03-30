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


#helper for getting address
def addy_extractor(src):
    arr = src.split(',')
    city = arr[0]
    prov_zip = arr[1].split(' ')
    if len(prov_zip) == 3:
        state = prov_zip[1]
        zip_code = prov_zip[2]
    
    return city, state, zip_code


def fetch_data():

    locator_domain = 'https://www.procuts.com/'

    ext = 'salonlocator/default.asp?state=all&city=BROWNSVILLE'
    ext2 = 'salonlocator/default.asp?state=all&city=CORPUS CHRISTI'

    to_scrape1 = locator_domain + ext
    page1 = session.get(to_scrape1)
    assert page1.status_code == 200

    soup = BeautifulSoup(page1.content, 'html.parser')
    pattern = re.compile('locations = ({"locations":.*);')
    script = soup.find("script", text=pattern)
    poi = json.loads(re.search(pattern, script.text).group(1))["locations"][0]

    lat = poi['latitude']
    longit = poi['longitude']

    store = soup.find('div', {'class': 'result_LocationContainer'})

    location_name = store.find('div', {'class': 'result_MallName'}).text

    street_address = store.find('div', {'class': 'result_Street'}).text
    city, state, zip_code = addy_extractor(store.find('div', {'class': 'result_Location'}).text)
    phone_number = store.find('div', {'class': 'result_Phone'}).text

    country_code = 'US'
    store_number = '<MISSING>'
    location_type = '<MISSING>'
    hours = '<MISSING>'

    sunrise_plaza = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                     store_number, phone_number, location_type, lat, longit, hours ]


    to_scrape2 = locator_domain + ext2
    page2 = session.get(to_scrape2)
    assert page2.status_code == 200

    soup = BeautifulSoup(page2.content, 'html.parser')

    soup = BeautifulSoup(page1.content, 'html.parser')
    pattern = re.compile('locations = ({"locations":.*);')
    script = soup.find("script", text=pattern)
    poi = json.loads(re.search(pattern, script.text).group(1))["locations"][0]
    lat = poi['latitude']
    longit = poi['longitude']


    store = soup.find('div', {'class': 'result_LocationContainer'})



    location_name = store.find('div', {'class': 'result_MallName'}).text

    street_address = store.find('div', {'class': 'result_Street'}).text
    city, state, zip_code = addy_extractor(store.find('div', {'class': 'result_Location'}).text)
    phone_number = store.find('div', {'class': 'result_Phone'}).text

    country_code = 'US'
    store_number = '<MISSING>'
    location_type = '<MISSING>'
    hours = '<MISSING>'

    cim_center = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                     store_number, phone_number, location_type, lat, longit, hours ]

        
    all_store_data = [sunrise_plaza, cim_center]
    
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
