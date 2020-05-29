import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import json
from sgselenium import SgSelenium
import time
import re

driver = SgSelenium().chrome()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation",
                         "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

session = SgRequests()

def fetch_data():
    # Your scraper here

    page_url = []

    driver.get("https://shop.carpetmart.com/store-locator")
    time.sleep(10)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    stores = soup.find_all('div', {'class': 'storelocator-store'})
    print(len(stores))
    all = []
    for store in stores:
        #print("here")
        url = store.find_all('a')[2].get('href')
        driver.get(url)
        #print(url)
        time.sleep(2)
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        js = soup.find_all('script', {'type': 'application/ld+json'})[-1].contents

        js = json.loads("".join(js))
        addr = js["address"]
        tim = ""
        left = soup.find_all('div', {'class': 'sp-hours-left'})
        right = soup.find_all('div', {'class': 'sp-hours-right'})
        for i in range(len(left)):
            tim += left[i].text.strip() + " " + right[i].text.strip() + " "
        coord = soup.find('div', {'class', 'sp-directions'}).find('a').get('href')
        # print(coord)
        lat = re.findall(r'!1d[-?\d\.]*!2d([-?\d\.]*)', coord)[0].replace("?", "")
        long = re.findall(r'!1d(-?[\d\.]*)', coord)[0].replace("?", "")
        # print(lat,long)
        """tim=""
        for t in js["openingHours"]:
            tim+= t+" "
        """
        all.append([
            "https://www.carpetmart.com/",
            url.split("/")[-1].replace("-", " "),
            addr["streetAddress"],
            addr["addressLocality"],
            addr["addressRegion"],
            addr["postalCode"].split("-")[0],
            "US",
            "<MISSING>",  # store #
            js["telePhone"],  # phone
            js["name"],  # type
            lat,  # lat
            long,  # long
            tim.strip(),  # timing
            url])

    return all

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
