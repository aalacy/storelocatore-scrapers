import csv
import re
from sgrequests import SgRequests
from bs4 import BeautifulSoup
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('hobbytown_com')


def addy_ext(addy):
    addy = addy.split(',')
    city = addy[0]
    state_zip = addy[1].strip().split(' ')
    state = state_zip[0]
    zip_code = state_zip[1]
    return city, state, zip_code

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():

    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36'
    HEADERS = {'User-Agent' : user_agent}
    session = SgRequests()

    locator_domain = 'https://www.hobbytown.com'

    payload = { 'zip': '52240', 
            'pageType': 'StoreLocator',
            'searchRadius': '3000', 
            'productID': '0'}

    base_link = "https://www.hobbytown.com/ajax/store-locations/store-list"
    response = session.post(base_link,headers=HEADERS,data=payload)
    base = BeautifulSoup(response.text,"lxml")

    all_scripts = base.find_all('script')
    for script in all_scripts:
        if "var options" in str(script):
            script = str(script)
            break
    geos = re.findall(r'[0-9]{2}\.[0-9]+, -[0-9]{2,3}\.[0-9]+',script)
    hrefs = base.find_all(title="Store Profile")

    link_list = []
    for h in hrefs:
        link = locator_domain + h['href']
        link_list.append(link)

    logger.info("Got %s links" %len(link_list))
      
    all_store_data = []
    for i, link in enumerate(link_list):
        logger.info(link)

        req = session.get(link, headers = HEADERS)
        base = BeautifulSoup(req.text,"lxml")

        location_name = base.h1.text.strip()
        
        addy = list(base.find(class_='col-12 location-contact').p.stripped_strings)
        street_address = addy[0]
        if "," in addy[1]:
            city, state, zip_code = addy_ext(addy[1])
            phone_number = addy[2].strip()
        else:
            street_address = street_address + " " + addy[1]
            city, state, zip_code = addy_ext(addy[2])
            phone_number = addy[3].strip()
        street_address = street_address.split("(")[0]
        
        hours = " ".join(list(base.find(class_="location-hours").stripped_strings)).replace("Store Hours","").strip()
        
        country_code = 'US'
        store_number = link.split("/")[-1].replace("l","")
        location_type = '<MISSING>'
        page_url = link

        geo = geos[i].split(",")
        lat = geo[0].strip()
        longit = geo[1].strip()

        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code, 
                    store_number, phone_number, location_type, lat, longit, hours, page_url]

        all_store_data.append(store_data)

    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
