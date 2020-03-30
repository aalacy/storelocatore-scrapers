import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json



session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }

    print("soup ===  first")

    base_url = "https://westshorepizza.com"
    r = session.get("https://westshorepizza.com/locations/", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    return_main_object = []
    #   data = json.loads(soup.find("div",{"paging_container":re.compile('latlong.push')["paging_container"]}))
    # for link in soup.find_all('ul',re.compile('content')):
    #     print(link)

    # it will used in store data.
    locator_domain = base_url
    location_name = ""
    street_address = ""
    city = ""
    state = ""
    zipp = ""
    country_code = ""
    store_number = "<MISSING>"
    phone = ""
    location_type = "italianvillagepizza"
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    hours_of_operation = ""

    for script in soup.find_all('div', {'class': 'geodir-content'}):
        street_address = script.find('span', {'itemprop': 'streetAddress'}).text
        location_name = script.find('span', {'itemprop': 'addressLocality'}).text
        city = script.find('span', {'itemprop': 'addressLocality'}).text
        state = script.find('span', {'itemprop': 'addressRegion'}).text
        zipp = script.find('span', {'itemprop': 'postalCode'}).text
        phone = script.find('a', {'href': re.compile("tel:")}).text
        country_code = 'US'

        try:
            hours_of_operation = ','.join(script.find('div', {'class': re.compile('geodir_timing')}).stripped_strings)
        except:
            hours_of_operation = "<MISSING>"
            pass

        store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                 store_number, phone, location_type, latitude, longitude, hours_of_operation]

        # print("data = " + str(store))
        # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')

        return_main_object.append(store)

    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)


scrape()
