import csv
import time
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('fresh_com')




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
countries = {}

def fetch_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
        # 'Content-Type': 'application/x-www-form-urlencoded',
    }

    addresses = []
    base_url = "https://www.fresh.com"
    # logger.info(base_url)
    locator_domain = base_url
    location_name = ""
    street_address = ""
    city = ""
    state = ""
    zipp = ""
    country_code = ""
    store_number = ""
    phone = ""
    location_type = ""
    latitude = ""
    longitude = ""
    hours_of_operation = ""
    page_url = ""

    r = session.get("https://www.fresh.com/us/customer-service/USShops.html", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    links = soup.find_all("p",{"class":"subheader1 privacy-info-question"})
    for link in links:
        page_url = link.find("a")['href']
        
        page_r = session.get(page_url, headers=headers)
        page_soup = BeautifulSoup(page_r.text, "lxml")
        location_name = link.find("a").text

        addr_json = json.loads(page_soup.find(lambda tag : (tag.name == "script") and "AggregateRating" in tag.text).text)
        street_address = addr_json['address']['streetAddress'].replace("\n"," ").strip()
        city = addr_json['address']['addressLocality']
        state = addr_json['address']['addressRegion']
        zipp = addr_json['address']['postalCode']
        country_code = addr_json['address']['addressCountry']
        phone = addr_json['telephone']
        latitude = page_soup.find("img",{"alt":"Map"})['src'].split("center=")[1].split("%2C")[0]
        longitude = page_soup.find("img",{"alt":"Map"})['src'].split("%2C")[1].split("&language")[0]
        hours_of_operation = " ".join(list(page_soup.find("tbody",{"class":"lemon--tbody__373c0__2T6Pl"}).stripped_strings)).replace("Closed now","").strip()

    
        store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                 store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]

        if str(store[2]) not in addresses:
            addresses.append(str(store[2]))

            store = [x.strip() if x else "<MISSING>" for x in store]

            # logger.info("data = " + str(store))
            # logger.info('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
            yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
