import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

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
    time.sleep(2)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    stores = soup.find_all('div', {'class': 'storelocator-store'})
    print(len(stores))
    all=[]
    for store in stores:
        print("here")
        url=store.find_all('a')[2].get('href')
        driver.get(url)
        print(url)
        #time.sleep(5)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        driver.switch_to.frame(driver.find_element_by_class_name("storepage-map").find_element_by_tag_name('iframe'))
        time.sleep(5)
        #driver.switch_to.frame("/html/body/div[1]/div[4]/div[1]/section/div[2]/div/div/div[3]/div/div[1]/div[4]/div[1]/iframe")
        coord=driver.find_element_by_class_name('google-maps-link').find_element_by_tag_name('a').get_attribute('href')
        print(coord)
        lat=0
        long=0
        js = soup.find_all('script', {'type': 'application/ld+json'})[-1].contents

        js=json.loads("".join(js))
        addr=js["address"]



        all.append([
        "https://www.carpetmart.com/",
        js["name"],
        addr["streetAddress"],
        addr["addressLocality"],
        addr["addressRegion"],
        addr["postalCode"].split("-")[0],
        "US",
        "<MISSING>",  # store #
        js["telephone"],  # phone
        js["@type"],  # type
        lat,  # lat
        long,  # long
        js["openingHours"].replace("Mo","Monday").replace("Tu","Tuesday").replace("We","Wednesday").replace("Th","Thursday").replace("Fr","Friday").replace("Sa","Saturday").replace("Su","Sunday") , # timing
        url])

    return all


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
