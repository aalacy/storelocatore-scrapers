import re
import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import json
from urllib.parse import urljoin
from lxml import html


def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    session = SgRequests()
    base_url = "https://kangarooexpress.com/store-locator"
    locator_domain = "kangarooexpress.com"
    data = []
    body = session.get(base_url).text
    sel = html.fromstring(body).xpath('//script/text()[contains(., "locations = ")]')[0].replace('\n','')
    js_st = "[{}]".format(re.findall(r'.+?locations = \[(.+?)\];', sel)[0].strip())
    json_body = json.loads(js_st.replace('"', '\\"').replace('\'', '"').replace('  ', '').replace(',}','}').replace(',]',']'))
    for result in json_body:
        status = result.get('status', '')
        if status == "Open":
            location_name = '<MISSING>'
            store_number = result.get('store_number', '')
            latitude = result.get('lat', '')
            longitude = result.get('lon', '')
            raw_address = BeautifulSoup(result["html"],"lxml")
            street_address = raw_address.find(class_="location data-point").div.text.strip()
            city_line = raw_address.find(class_="location data-point").find_all('div')[1].text.split(",")
            city = city_line[0].strip().title()
            state = city_line[1].strip()
            zip_code = city_line[2].strip()
            country_code = "US"

            # html_ = html.fromstring(result.get('html', ''))
            # href = html_.xpath('//a[contains(text(), "Location Details")]/@href')
            # if href:
            #     url = urljoin(base_url, href[0])
            #     base = session.get(url).text

            location_type = '<MISSING>'
            hours_of_operation = '<MISSING>'
            phone = '<MISSING>'
            
            data.append([locator_domain, base_url, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])

    return data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
