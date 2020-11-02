import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import time

session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
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

    base_link = 'http://www.procuts.com/salonlocator/default.asp'
    locator_domain = 'procuts.com'

    page = session.get(base_link)
    time.sleep(2)
    assert page.status_code == 200

    all_store_data = []
    soup = BeautifulSoup(page.content, 'html.parser')
    results = soup.find(id="result_CityList").find_all("li")
    for result in results:
        link = "http://www.procuts.com/salonlocator/" + result['onclick'].split('location=')[-1].replace("'","")

        page = session.get(link)
        time.sleep(2)
        assert page.status_code == 200
        soup = BeautifulSoup(page.content, 'html.parser')

        pattern = re.compile('locations = ({"locations":.*);')
        script = soup.find("script", text=pattern)
        poi = json.loads(re.search(pattern, script.text).group(1))["locations"][0]

        lat = poi['latitude']
        longit = poi['longitude']

        store = soup.find('div', {'class': 'result_LocationContainer'})

        location_name = "PROCUTS - " + store.find('div', {'class': 'result_MallName'}).text

        street_address = store.find('div', {'class': 'result_Street'}).text
        city, state, zip_code = addy_extractor(store.find('div', {'class': 'result_Location'}).text)
        phone_number = store.find('div', {'class': 'result_Phone'}).text

        country_code = 'US'
        store_number = poi["salonid"]
        location_type = '<MISSING>'

        final_link = "http://www.procuts.com/salondetail/default.asp?salonid=" + store_number

        final_page = session.get(final_link)
        time.sleep(2)
        assert final_page.status_code == 200
        final_soup = BeautifulSoup(final_page.content, 'html.parser')

        raw_hours = final_soup.find(id="detailC").text
        hours = raw_hours.replace("\n"," ").replace("PM","PM ").strip()
        hours_of_operation = (re.sub(' +', ' ', hours)).strip()

        if not hours_of_operation:
            hours_of_operation = "<MISSING>"


        all_store_data.append([locator_domain, final_link, location_name, street_address, city, state, zip_code, country_code,
                         store_number, phone_number, location_type, lat, longit, hours_of_operation])
    
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
