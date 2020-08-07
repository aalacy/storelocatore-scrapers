import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import unicodedata
import time
from random import randint

from sgselenium import SgSelenium


def addy_ext(addy):
    addy = addy.split(',')
    city = addy[0]
    state_zip = addy[1].strip().split(' ')
    state = state_zip[0]
    zip_code = state_zip[1]
    return city, state, zip_code

def write_output(data):
    with open('data.csv', 'w') as output_file:
        writer = csv.writer(output_file, delimiter=",")

        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        for i in data or []:
            writer.writerow(i)

def fetch_data():

    base_link = "https://fit4lifehealthclubs.com/find-a-gym/"

    driver = SgSelenium().chrome()
    time.sleep(2)

    driver.get(base_link)
    time.sleep(randint(15,20))
    soup = BeautifulSoup(driver.page_source, "lxml")

    session = SgRequests()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }

    
    all_store_data = []

    k = soup.find_all(class_='wpgmp_locations')
    for i in k:
        store = []
        if "coming soon" in i.text.lower():
            continue
        link = i.find_all("a")[-1]['href']
        print(link)
        location_name= i.find_all("a")[-2].text
        raw_address = i.find(class_="wpgmp_locations_content").text.strip().split("\n")
        try:
            address = (raw_address[-5] + " " + raw_address[-4]).strip()
        except:
            address = raw_address[-4]

        city, state, zip1 = addy_ext(raw_address[-3])
        phone = raw_address[-2]

        r1 = session.get(link, headers=headers)
        soup1 = BeautifulSoup(r1.text, "lxml")
        try:
            lng = soup1.find_all('iframe')[1]['src'].split('!2d')[1].split('!3d')[0]
            lat = soup1.find_all('iframe')[1]['src'].split('!2d')[1].split('!3d')[1].split('!')[0]
        except:
            continue
        raw_hours = soup1.find_all('div', {'class': re.compile(r'wpb_text_column wpb_content_element vc_custom_[0-9]+')})[-2].p.text.strip()
        hour = raw_hours.replace('\n','').strip().replace('\xa0','').replace("pm","pm ").strip()
        store.append('https://fit4lifehealthclubs.com/')
        store.append(location_name)
        store.append(address)
        store.append(city)
        store.append(state) 
        store.append(zip1)
        store.append('US')
        store.append("<MISSING>")
        store.append(phone)
        store.append("<MISSING>")
        store.append(lat)
        store.append(lng)
        store.append(hour)
        store.append(link)
        all_store_data.append(store)

    driver.close()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)


scrape()
