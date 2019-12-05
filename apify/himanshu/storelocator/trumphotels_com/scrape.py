import csv
import requests
from bs4 import BeautifulSoup
import re
import json
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import time
import platform

system = platform.system()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def get_driver():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=1920,1080')
    if "linux" in system.lower():
        return webdriver.Firefox(executable_path='./geckodriver', options=options)
    else:
        return webdriver.Firefox(executable_path='geckodriver.exe', options=options)

def fetch_data():
    driver = get_driver()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }
    addresses = []
    base_url = "https://www.trumphotels.com/"
    driver.get('https://www.trumphotels.com/')
    soup = BeautifulSoup(driver.page_source, "lxml")
    for country in soup.find("div",{"id":"ourhotels"}).find_all("div",{"class":"filterlist"}):
        for location in country.find_all("a"):
            driver.get(base_url + location["href"])
            location_soup = BeautifulSoup(driver.page_source,"lxml")
            for script in location_soup.find_all("script",{"type":"application/ld+json"}):
                if "address" in json.loads(script.text):
                    store_data = json.loads(script.text)
                    if store_data["address"]["addressCountry"] not in ("USA","Canada"):
                        continue
                    name = location.text.strip()
                    address = store_data["address"]
                    geo_location = location_soup.find("div",{"class":"map-outer-div"})
                    store = []
                    store.append("https://www.trumphotels.com")
                    store.append(name.replace("®",""))
                    store.append(address["streetAddress"])
                    store.append(address["addressLocality"].split(",")[0])
                    store.append(address["addressRegion"] if "addressRegion" in address else address["addressLocality"].split(",")[1])
                    store.append(address["postalCode"])
                    store.append("US" if address["addressCountry"] == "USA" else "CA")
                    store.append("<MISSING>")
                    store.append(store_data["telephone"] if store_data["telephone"] else "<MISSING>")
                    store.append("<MISSING>")
                    store.append(geo_location["data-latitude"])
                    store.append(geo_location["data-longitude"])
                    store.append("<MISSING>")
                    store.append("<MISSING>")
                    yield store

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
