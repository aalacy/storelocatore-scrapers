from sgrequests import SgRequests
from bs4 import BeautifulSoup
import csv
import time
from random import randint
import re

from selenium import webdriver
from selenium.webdriver.chrome.options import Options


def get_driver():
    options = Options() 
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=1920,1080')
    return webdriver.Chrome('chromedriver', chrome_options=options)


def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)


def fetch_data():
    output_list = []

    url = "https://www.sunriserecords.com/locations/"

    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
    HEADERS = {'User-Agent' : user_agent}

    session = SgRequests()
    req = session.get(url, headers = HEADERS)
    time.sleep(randint(1,2))
    try:
        base = BeautifulSoup(req.text,"lxml")
        print("Got today page")
    except (BaseException):
        print('[!] Error Occured. ')
        print('[?] Check whether system is Online.')

    driver = get_driver()
    time.sleep(2)

    states = base.find_all(class_="loc-header")
    store_tables = base.find(class_="locations-cont").find_all("table")
    
    for i, store_table in enumerate(store_tables):
        raw_state = states[i].text.strip()
        rows = store_table.find_all("tr")
        stores = []
        for row in rows:
            stores.append(row)

        for store in stores:
            try:
                location_name = store.find("td").text.strip()
                print(location_name)
            except:
                continue

            raw_address = store.find_all("td")[1].text.replace("J1L1K1", ", J1L 1K1").replace("SK S7K","S7K")
            street_address = raw_address[:raw_address.rfind(",")].strip()
            raw_city = store.find_all("td")[2].text.strip()
            if raw_state == "Atlantic Canada":
                state = raw_city[-3:].strip()
                city = raw_city[:raw_city.find(",")]
            else:
                city = raw_city
                state = raw_state
                
            try:
                map_link = store.find_all("td")[4].a['href']
                at_pos = map_link.rfind("@")
                latitude = map_link[at_pos+1:map_link.find(",", at_pos)].strip()
                longitude = map_link[map_link.find(",", at_pos)+1:map_link.find(",", at_pos+15)].strip()

                if not latitude[:2].isnumeric():
                    driver.get(map_link)
                    time.sleep(7)

                    try:
                        map_link = driver.current_url
                        at_pos = map_link.rfind("@")
                        latitude = map_link[at_pos+1:map_link.find(",", at_pos)].strip()
                        longitude = map_link[map_link.find(",", at_pos)+1:map_link.find(",", at_pos+15)].strip()
                    except:
                        latitude = "<INACCESSIBLE>"
                        longitude = "<INACCESSIBLE>"
            except:
                latitude = "<MISSING>"
                longitude = "<MISSING>"

            if street_address == "2102 11th Ave":
                latitude = 50.4506685
                longitude = -104.6127555

            output = []
            output.append("sunriserecords.com") # locator_domain
            output.append(url) # url
            output.append(location_name) #location name
            output.append(street_address) #address
            output.append(city) #city
            output.append(state) #state
            output.append(raw_address[raw_address.rfind(",")+1:].strip()) #zipcode
            output.append('CA') #country code
            output.append("<MISSING>") #store_number
            output.append(store.find_all("td")[3].text.strip()) #phone
            output.append("<MISSING>") #location type
            output.append(latitude) #latitude
            output.append(longitude) #longitude
            output.append("<MISSING>") #opening hours
            output_list.append(output)

    try:
        driver.close()
    except:
        pass

    return output_list

def scrape():
    data = fetch_data()
    write_output(data)

scrape()

