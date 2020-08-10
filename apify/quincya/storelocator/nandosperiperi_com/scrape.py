from sgrequests import SgRequests
from bs4 import BeautifulSoup
import csv
import time
from random import randint


def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():

    base_link = "https://www.nandosperiperi.com/find"

    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
    HEADERS = {'User-Agent' : user_agent}

    session = SgRequests()
    req = session.get(base_link, headers = HEADERS)
    time.sleep(randint(1,2))
    try:
        base = BeautifulSoup(req.text,"lxml")
        print("Got today page")
    except (BaseException):
        print('[!] Error Occured. ')
        print('[?] Check whether system is Online.')

    data = []

    locator_domain = "nandosperiperi.com"
    states = base.find_all(class_="state")
    for state_item in states:        
        items = state_item.find_all(class_="city-info")
        for item in items:
            location_name = item.h3.text
            print(location_name)

            raw_address = item.p.text.replace("\t","").replace("\n","").split(",")
            street_address = raw_address[0].strip()
            city = raw_address[1].strip()
            state = state_item.h2.text.replace("Washington, DC","DC")
            zip_code = raw_address[-1][-6:].strip()

            country_code = "US"
            store_number = "<MISSING>"
            location_type = "<MISSING>"

            phone = item['data-tel']
            latitude = item['data-lat']
            longitude = item['data-lng']
            link = item['data-link']
            req = session.get(link, headers = HEADERS)
            base = BeautifulSoup(req.text,"lxml")
            hours_of_operation = base.find(class_="collapseBox-info").text.replace("\n","").strip()

            data.append([locator_domain, link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])

    return data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
