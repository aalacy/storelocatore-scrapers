from sgrequests import SgRequests
from bs4 import BeautifulSoup
import csv

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():

    locator_domain = 'https://www.revuup.com/'

    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
    HEADERS = {'User-Agent' : user_agent}

    session = SgRequests()
    req = session.get(locator_domain, headers = HEADERS)
    base = BeautifulSoup(req.text,"lxml")

    exts = base.find(id="menu-item-68").find_all("li")

    all_store_data = []
    for ext in exts:
        link = ext.a["href"]
        req = session.get(link, headers = HEADERS)
        base = BeautifulSoup(req.text,"lxml")

        main = base.find(id='studios_address')

        location_name = base.h2.text.strip()
        content = main.text.split('\n')
        street_address = content[1]
        city_state = content[2].split(',')
        city = city_state[0]
        state = city_state[1].split()[0].strip()
        zip_code = city_state[1].split()[1].strip()
        phone_number = content[3].replace("p.","").strip()

        map_link = base.find(id='studios_map').iframe['src']
        lat_pos = map_link.rfind("!3d")
        lat = map_link[lat_pos+3:map_link.find("!",lat_pos+5)].strip()
        lng_pos = map_link.find("!2d")
        longit = map_link[lng_pos+3:map_link.find("!",lng_pos+5)].strip()

        country_code = 'US'
        store_number = '<MISSING>'
        location_type = '<MISSING>'
        hours = '<MISSING>'

        store_data = [locator_domain, link, location_name, street_address, city, state, zip_code, country_code,
                      store_number, phone_number, location_type, lat, longit, hours]
        all_store_data.append(store_data)

    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
