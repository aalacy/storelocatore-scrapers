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
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)
def fetch_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    base_url = "https://www.sageveganbistro.com"
    r = session.get("https://www.sageveganbistro.com/our-story/#locations", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
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
    location_type = "sageveganbistro"
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    for script in soup.find_all("div", {"class": "sqs-block-content"}):
        if len(list(script.stripped_strings)) >= 6:
            
            address_list = list(script.stripped_strings)
            if "View fullsize" in address_list or "Thank you!" in address_list or "UberEats" in address_list :
                continue
            location_name = address_list[0]
            street_address = address_list[1]
            city = address_list[2].split(',')[0]
            state = address_list[2].split(',')[1].strip().split(' ')[0]
            zipp = address_list[2].split(',')[1].strip().split(' ')[1]
            phone = address_list[3]
            hour = " ".join(address_list[5:])
            page_url = "https://www.sageveganbistro.com/contact"
            store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                        store_number, phone, location_type, latitude, longitude, hour,page_url]
            yield store
def scrape():
    data = fetch_data()
    write_output(data)
scrape()
