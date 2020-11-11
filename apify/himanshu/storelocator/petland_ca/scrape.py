import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json

session = SgRequests()

session = SgRequests()
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('petland_ca')


def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    base_url = "https://petland.com/"
    headers = {
        "Accept": "application/xml, text/xml, */*; q=0.01",
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.122 Safari/537.36',
    }
    r = session.get("https://petland.com/stores/map/locations.xml", headers=headers)
    soup = BeautifulSoup(r.text , "lxml")
    for data in soup.find_all("marker"):
        location_name = data['name']
        street_address = (data['address'] +" "+ str(data['address2'])).strip()
        city = data['city']
        state = data['state']
        zipp = data['postal']
        phone = data['phone']
        country_code = "US"
        location_type = data['category']
        latitude = data['lat']
        longitude = data['lng']
        page_url = data['web']
        try:
            r1 = session.get(page_url, headers=headers)
            soup1 = BeautifulSoup(r1.text, "lxml")
        except:
            pass
        try:
            hours = (re.sub(r'\s+'," ",str(" ".join(list(soup1.find_all("div",{"class":"clearfix"})[-1].find("strong").stripped_strings))))).split("Holiday Hours:")[0].replace("Petland Southpoint","").replace("Petland Vineyard","")
        except:
            hours = "<MISSING>"
        if page_url == "http://www.petlandflorida.com":
            hours = "Monday - Sunday 10:00 am - 9:00 pm"
        store = []
        store.append(base_url)
        store.append(location_name)
        store.append(street_address)
        store.append(city)
        store.append(state)
        store.append(zipp)
        store.append(country_code)
        store.append("<MISSING>")
        store.append(phone)
        store.append(location_type)
        store.append(latitude)
        store.append(longitude)
        store.append(hours.strip())
        store.append(page_url)
        # logger.info("data ==="+str(store))
        # logger.info("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        yield store
    

    
        


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
