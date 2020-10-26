import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import urllib3

session = SgRequests()

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }

    addresses = []

    base_url = "https://www.hyperionpublic.com"
    r = session.get("https://hyperionpublic.site/wp-json/tribe/events/v1/events/?start_date=today&end_date=+2%20days").json()
    for data in r['events']:
        location_name = "<MISSING>"
        street_address = data['venue']['address']
        city = data['venue']['city']
        state = data['venue']['state']
        zipp = data['venue']['zip']
        country_code = "US"
        store_number = data['venue']['id']
        phone = data['venue']['phone']
        location_type = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        if "website" in data['venue']:
            page_url = data['venue']['website']
        else:
            page_url = "http://hyperionpublic.com/silver-lake"

        if "silver-lake" in page_url:
            hours = "RESTAURANT : Monday11AM10PM Tuesday11AM10PM Wednesday11AM10PM Thursday11AM11PM Friday11AM11PM Saturday 9AM11PM Sunday 9AM10PM COMMUNITY PUB : Monday 4PM2AM Tuesday 4PM2AM Wednesday 4PM2AM Thursday 4PM2AM Friday 4PM2AM Saturday 9AM2AM Sunday 9AM2AM"
        else:
            hours = "<MISSING>"
        if "Studio City" in city.strip():
            continue
        store = []
        store.append(base_url)
        store.append(location_name)
        store.append(street_address)
        store.append(city)
        store.append(state)
        store.append(zipp)
        store.append("US")
        store.append(store_number)
        store.append(phone)
        store.append(location_type)
        store.append(latitude)
        store.append(longitude)
        store.append(hours)
        store.append(page_url)
        if store[2] in  addresses:
            continue
        addresses.append(store[2])
        yield store
        # print(store)

def scrape():
    data = fetch_data()
    write_output(data)


scrape()
