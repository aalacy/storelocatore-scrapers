import requests
import csv
from bs4 import BeautifulSoup
import re
import json
import usaddress

DOMAIN = "http://pic-n-pac.com"
MISSING = "<MISSING>"

def write_output(data):
    with open('data.csv', mode='w', encoding='utf-8', newline='') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    data=[]
    url = "http://pic-n-pac.com/locations/"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    loc_data = soup.findAll('script', attrs = {'type':'text/javascript'})
    for loc in loc_data:
        try:
            if "var wpgmaps_localize_marker_data" in loc.text:
                jsn = re.findall('\{\"map_id\":\"1\".*\"other_data\":\"\"\}', loc.text)
                parse = re.split(',\"[0-9]+\"\:', str(jsn[0]))
                for j in parse:
                    js = json.loads(j)
                    location_name = js['title']
                    if location_name == '':
                        location_name = MISSING
                    ad = js['address'].strip()
                    ad_list = re.split(' ', ad)
                    street_address = ' '.join(ad_list[:-3])
                    if "United States" in ad:
                        street_address = re.split(",", ad)[0]
                    tagged = usaddress.tag(ad)[0]
                    zipcode = tagged['ZipCode'].strip()
                    state = tagged['StateName'].strip()
                    city = tagged['PlaceName'].strip()
                    lat = js['lat'].strip()
                    lon = js['lng'].strip()
                    store_number = location_type = store_number = phone = hours_of_operation = MISSING
                    data.append([DOMAIN, location_name, street_address, city, state, zipcode, 'US', store_number, phone, location_type, lat, lon, hours_of_operation])
        except requests.exceptions.RequestException:
            pass

    return data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
