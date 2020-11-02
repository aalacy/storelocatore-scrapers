import csv
import time

from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('familiadental_com')


 



session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation",
                         "page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }

    base_url = "https://www.familiadental.com"
    addresses = []

    r = session.get("https://www.familiadental.com/locations/", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")

    for script in soup.find_all(class_="page_item")[2:]:

        location_url = base_url + script.find("a")["href"]
        # logger.info("page_url === "+ location_url)
        r_location = session.get(location_url, headers=headers)
        soup_location = BeautifulSoup(r_location.text, "lxml")

        locator_domain = base_url
        location_name = ""
        street_address = ""
        city = ""
        state = ""
        zipp = ""
        country_code = "US"
        store_number = ""
        phone = ""
        location_type = ""
        latitude = ""
        longitude = ""
        raw_address = ""
        hours_of_operation = ""
        page_url = location_url

        full_address_url = soup_location.find(class_="layout-map").find("iframe")["data-map-src"]
        # logger.info("full_address_url == "+ full_address_url)
        geo_request = session.get(full_address_url, headers=headers)
        geo_soup = BeautifulSoup(geo_request.text, "lxml")
        for script_geo in geo_soup.find_all("script"):
            if "initEmbed" in script_geo.text:
                geo_data = json.loads(script_geo.text.split("initEmbed(")[1].split(");")[0])[21][3][0][1]
                lat = json.loads(script_geo.text.split("initEmbed(")[1].split(");")[0])[21][3][0][2][0]
                lng = json.loads(script_geo.text.split("initEmbed(")[1].split(");")[0])[21][3][0][2][1]

                # logger.info("geo_data ===== "+ geo_data)
                if len(geo_data.split(",")) > 3:
                    street_address = geo_data.split(',')[1]
                    city = geo_data.split(',')[2]
                else:
                    street_address = geo_data.split(',')[0]
                    city = geo_data.split(',')[1]

                state = geo_data.split(',')[-1].strip().split(" ")[0]
                zipp = geo_data.split(',')[-1].strip().split(" ")[-1]
                latitude = str(lat)
                longitude = str(lng)

        location_name = "Familia Dental " + soup_location.h1.text.strip()
        phone = soup_location.find("a",{"class":"main-btn3 transition"}).text.strip()
        hours_of_operation = soup_location.find("div",{"class":"hours-box"}).text.replace("Office Hours","").replace("—","-").strip()
        hours_of_operation = (re.sub(' +', ' ', hours_of_operation)).strip()

        # logger.info("street_address === "+street_address)
        store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]

        if str(store[2]) not in addresses:
            addresses.append(str(store[2]))

            store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]

            # logger.info("data = " + str(store))
            # logger.info('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
            yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
