import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import html5lib
session = SgRequests()
def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_ALL)
        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", 'page_url'])
        # Body
        for row in data:
            writer.writerow(row)
def fetch_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    base_url = "https://sambabraziliansteakhouse.com"
    return_main_object = []
    locator_domain = base_url
    location_name = ""
    street_address = "<MISSING>"
    city = "<MISSING>"
    state = "<MISSING>"
    zipp = "<MISSING>"
    country_code = "US"
    store_number = "<MISSING>"
    phone = "<MISSING>"
    location_type = "<MISSING>"
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    hours_of_operation = "<MISSING>"
    page_url = base_url
    r = session.get("https://sambabraziliansteakhouse.com/", headers=headers)
    soup = BeautifulSoup(r.text, "html5lib")
    script = soup.find_all('script', {'type': 'application/json'})[1]
    json_script = json.loads(script.text)
    for location in json_script['preloadQueries']:
        data = location['data']['restaurant']['homePage']['sections']
        for loc_list in data:
            loc = loc_list['locations']
            if loc != []:
                for l1 in loc:
                    location_name = l1['name']
                    street_address = l1['streetAddress']
                    city = l1['city']
                    state = l1['state']
                    zipp = l1['postalCode']
                    country_code = l1['country']
                    store_number = l1['id']
                    phone = l1['phone']
                    location_type = "<MISSING>"
                    latitude = l1['lat']
                    longitude = l1['lng']
                    hours_of_operation = " ".join(l1['schemaHours']).replace('Su', 'Sun').replace('Mo', 'Mon').replace(
                        'Tu', 'Tue').replace('We', 'Wed').replace('Th', 'Thu').replace('Fr', 'Fri').replace('Sa', 'Sat').strip()
                    page_url = base_url
                    store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                             store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]
                    return_main_object.append(store)
                return return_main_object
def scrape():
    data = fetch_data()
    write_output(data)
scrape()
