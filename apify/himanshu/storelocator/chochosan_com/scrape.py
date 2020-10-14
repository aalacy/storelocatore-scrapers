import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import ast
import time
from random import randint
from sgselenium import SgSelenium

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():

    driver = SgSelenium().chrome()
    time.sleep(2)

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'
    }
    base_url = "https://www.chochosan.com/location"
    r = session.get(base_url, headers=headers)
    soup = BeautifulSoup(r.text, "lxml")

    base_url1 = "https://www.chochosan.com/location-map"
    r = session.get(base_url1, headers=headers)
    soup1 = BeautifulSoup(r.text, "lxml")

    stores1 = soup1.find(id="comp-jspg5178").text.replace("\n"," ").replace("\xa0"," ")
    stores1 = stores1[stores1.find("Hours")+5:].strip()
    stores2 = soup1.find(id="comp-jspgftft").text.replace("\n"," ").replace("\xa0"," ")
    stores2 = stores2[stores2.find("Hours")+5:].strip()
    stores3 = soup1.find(id="comp-jsqntvax").text.replace("\n"," ").replace("\xa0"," ")
    stores3 = stores3[stores3.find("Hours")+5:].strip()
    stores4 = soup1.find(id="comp-jspg5178").text.replace("\n"," ").replace("\xa0"," ")
    stores4 = stores4[stores4.find("Hours")+5:].strip()

    hours = [stores1,stores2,stores3,stores4]
    lats = []
    lngs = []
    store_name = []
    store_detail = []
    return_main_object = []

    # Get lat/lng
    # print(base_url1)
    driver.get(base_url1)
    element = WebDriverWait(driver, 20).until(EC.presence_of_element_located(
        (By.ID, "SITE_HEADER")))
    time.sleep(randint(10,12))
    for i in range(4):
        map_frame = driver.find_elements_by_tag_name("iframe")[i]
        driver.switch_to.frame(map_frame)
        time.sleep(randint(1,2))
        map_str = driver.page_source
        geo = re.findall(r'[0-9]{2}\.[0-9]+,-[0-9]{2,3}\.[0-9]+',map_str)[0].split(",")
        lats.append(geo[0])
        lngs.append(geo[1])
        driver.switch_to_default_content()
        time.sleep(randint(1,2))    

    stores = soup.find_all(
        "div", {"class": "txtNew", "data-packed": "false", "data-min-height": "106"})

    for num,i in enumerate(stores):
        tem_var = []
        phone = list(i.stripped_strings)[-1]
        city_line = -2
        if "-" not in phone:
            phone = "<MISSING>"
            city_line = -1
        
        st = " ".join(list(i.stripped_strings)[2:city_line])
        if ")" in st:
            st = st[st.find(")")+1:].strip()
        city = list(i.stripped_strings)[city_line].split(',')[0].strip()
        state = list(i.stripped_strings)[city_line].split(',')[1].split()[0].strip()
        zipp = list(i.stripped_strings)[city_line].split(',')[1].split()[1].strip()
        name = list(i.stripped_strings)[0]
        if "San" in name:
            name = name + " " + city
        store_name.append(name)

        tem_var.append(st)
        # print(tem_var[0])
        tem_var.append(city)
        tem_var.append(state)
        tem_var.append(zipp)
        tem_var.append("US")
        tem_var.append("<MISSING>")
        tem_var.append(phone)
        tem_var.append("<MISSING>")
        tem_var.append(lats[num])
        tem_var.append(lngs[num])
        store_detail.append(tem_var)

    for i in range(len(store_name)):
        store = list()
        store.append("https://www.chochosan.com")
        store.append(store_name[i])
        store.extend(store_detail[i])
        store.append(hours[i])
        store.append("https://www.chochosan.com/location")
        return_main_object.append(store)
    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
