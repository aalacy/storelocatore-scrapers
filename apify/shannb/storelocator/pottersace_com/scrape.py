import csv
import requests
from bs4 import BeautifulSoup

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    # Your scraper here
    location_list = []
    base_url = "http://pottersace.com/page.asp?p=Store%20Locator"

    location_links = []
    location_name = None
    locator_domain = None
    street_address = None
    city = None
    state = None
    zip = None
    country_code = None
    store_number = "<MISSING>"
    phone = None
    location_type = "<MISSING>"
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    hours_of_operation = None

    soup = BeautifulSoup(requests.get(base_url).content, 'html.parser').find_all('table')[4].contents

    for content in soup:

        if type(content) is bs4.element.NavigableString:
            continue
        elif len(content.contents) > 1:

            print()
        elif len(content.contents) == 1:
            state = content.contents[0].get_text()

        else:
            continue
            

    #location_list.append([locator_domain, location_name, street_address, city, state, zip, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])
    return location_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
