import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import re


options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
driver = webdriver.Chrome("chromedriver", options=options)

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
    all=[]
    for store in stores:
        print("here")
        url=store.find_all('a')[2].get('href')
        driver.get(url)
        print(url)
        time.sleep(2)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
      

        js = soup.find_all('script', {'type': 'application/ld+json'})[-1].contents

        js=json.loads("".join(js))
        addr=js["address"]

        coord=soup.find('div',{'class','sp-directions'}).find('a').get('href')
        #print(coord)
        long = re.findall(r'!1d[-?\d\.]*!2d([-?\d\.]*)', coord)[0].replace("?","")
        lat = re.findall(r'!1d(-?[\d\.]*)', coord)[0].replace("?","")
        #print(lat,long)
        tim=""
        for t in js["openingHours"]:
            tim+= t+" "
        all.append([
        "https://www.carpetmart.com/",
        url.split("/")[-1],
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
        tim.strip().replace("Mo","Monday").replace("Tu","Tuesday").replace("We","Wednesday").replace("Th","Thursday").replace("Fr","Friday").replace("Sa","Saturday").replace("Su","Sunday") , # timing
        url])

    return all


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
