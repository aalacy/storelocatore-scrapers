import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import platform
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import time

session = SgRequests()

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
    headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    base_url = "http://www.worldpac.com"
    r = session.get("http://www.worldpac.com/js-css/locations.js?v=20150409.111800",headers=headers)
    return_main_object = []
    location_list = r.text.split("locations.push(")
    for i in range(2,len(location_list)-1):
        location_store = location_list[i].split(");")[0]
        street = location_store.split("street:")[1].split(",")[0]
        city = location_store.split("city:")[1].split(",")[0]
        state = location_store.split("state:")[1].split(",")[0]
        zip = location_store.split("zip:")[1].split(",")[0]
        country = location_store.split("country:")[1].split(",")[0]
        store = []
        store.append("http://www.worldpac.com")
        store.append(city.replace("'","") + "," + state.replace("'",""))
        store.append(street.replace("'","").replace("Ã¨"," "))
        store.append(city.replace("'",""))
        store.append(state.replace("'",""))
        store.append(zip.replace("'","")[1:] if zip.replace("'","") != "" else "<MISSING>")
        if store[-1] == "":
            store[-1] = '<MISSING>'
        if store[-1] == "<MISSING>":
            driver = get_driver()
            driver.get("http://maps.google.com/maps?q=" + str(store[2]))
            time.sleep(10)
            soup = BeautifulSoup(driver.page_source,"lxml")
            if soup.find("span",text=re.compile(r"[A-Z]{1}[0-9]{1}[A-Z]{1}\s*[0-9]{1}[A-Z]{1}[0-9]{1}")):
                text = soup.find("span",text=re.compile(r"[A-Z]{1}[0-9]{1}[A-Z]{1}\s*[0-9]{1}[A-Z]{1}[0-9]{1}")).text
                zip = re.findall(r'[A-Z]{1}[0-9]{1}[A-Z]{1}\s*[0-9]{1}[A-Z]{1}[0-9]{1}', str(text))[-1]
                store[-1] = zip
        store.append(country.replace("'",""))
        store.append("<MISSING>")
        store.append("<MISSING>")
        store.append("<MISSING>")
        store.append("<MISSING>")
        store.append("<MISSING>")
        store.append("<MISSING>")
        store.append("<MISSING>")
        yield store

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
