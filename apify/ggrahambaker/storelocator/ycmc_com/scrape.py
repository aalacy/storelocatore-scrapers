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

def addy_extractor(src):
    arr = src.split(',')
    city = arr[0]
    prov_zip = arr[1].strip().split(' ')
    state = prov_zip[0].strip()
    zip_code = prov_zip[1].strip()

    return city, state, zip_code

def fetch_data():
    locator_domain = 'ycmc.com'
    base_link = 'https://www.ycmc.com/locator'

    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
    HEADERS = {'User-Agent' : user_agent}

    session = SgRequests()
    req = session.get(base_link, headers = HEADERS)
    base = BeautifulSoup(req.text,"lxml")

    divs = base.find_all(class_='ycmc_store_detail')

    all_store_data = []
    for div in divs:

        ps = div.find_all('p')

        location_name = ps[0].text.strip()

        addy = ps[1].text.strip().split('\n')

        street_address = addy[0].strip()
        city, state, zip_code = addy_extractor(addy[1].strip())
        phone_number = addy[2].strip().replace('Phone:', '').strip()

        hour_split = ps[2].text.strip().split('\n')
        hours = hour_split[1].strip() + ' ' + hour_split[2].strip()

        country_code = 'US'
        location_type = '<MISSING>'
        store_number = '<MISSING>'
        lat = '<MISSING>'
        longit = '<MISSING>'

        loc_text = str(base.find(class_="std").find("script"))
        raw_loc = loc_text[loc_text.find("[")+1:loc_text.rfind("];")].strip()
        locs = raw_loc.split("\r\n\r\n")
        for loc in locs:
            if phone_number in loc:
                lat = loc.split("\r\n")[-2][1:-2]
                longit = loc.split("\r\n")[-1][1:-3]
                break
        if "11500 Midlothian Turnpike" in street_address:
            lat = "37.507149"
            longit = "-77.608657"
        if "4020 Victory Blvd" in street_address:
            lat = "36.810275"
            longit = "-76.357686"
        if "8649 Philadelphia Road" in street_address:
            lat = "39.335366"
            longit = "-76.527934"

        store_data = [locator_domain, base_link, location_name, street_address, city, state, zip_code, country_code,
                      store_number, phone_number, location_type, lat, longit, hours]

        all_store_data.append(store_data)
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
