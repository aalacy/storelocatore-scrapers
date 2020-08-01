import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
from selenium import webdriver
import time
import html
import platform

session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    # pass
    r = session.get("http://www.wagner-oil.com/store-locator/")
    soup = BeautifulSoup(r.text, "lxml")
    # print(soup.prettify())
    # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~`')
    phone_tag = []
    city_tag = []
    st = []
    name_ran = []
    k = soup.find('table').find_all("div",{"align":"center"})[1]
    for i in k.find_all('tr'):
        data = (list(i.stripped_strings))
        # print(data)
        if len(data) == 4:
            name_ran.append(data[1])
            st.append(data[2])
            phone_tag.append(data[3])
            city_tag.append(data[0])
    for i in range(len(name_ran)):
        locator_domain = "http://www.wagner-oil.com/"
        street_address = st[i]
        name = name_ran[i]
        city = city_tag[i]
        state = "<MISSING>"
        store_zip = "<MISSING>"
        phone = phone_tag[i]
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        country_code = "US"
        location_type = "<MISSING>"
        store_number = "<MISSING>"
        hours_of_operation = "<MISSING>"
        page_url = "http://www.wagner-oil.com/store-locator/"
        store = [locator_domain, name, street_address, city, state, store_zip, country_code,
                    store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]
        store = ["<MISSING>" if x == "" or x == None else x for x in store]
        store = [str(x).encode('ascii', 'ignore').decode(
            'ascii').strip() if x else "<MISSING>" for x in store]
        yield store

def scrape():
    data = fetch_data()
    write_output(data)


scrape()
