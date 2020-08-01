import csv
from bs4 import BeautifulSoup
import re
import json
import ssl
from sgselenium import SgSelenium
import time
from selenium.webdriver.support.wait import WebDriverWait
import unicodedata


def write_output(data):
    with open('data.csv', mode='w',newline="") as output_file:
        writer = csv.writer(output_file, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    driver = SgSelenium().firefox()
    base_url = "https://www.godandy.com/"

    soup = BeautifulSoup(driver.page_source, "lxml")
    # print(soup)

    for number in range(1,70):
        page_url = "https://www.godandy.com/store_details.cfm?Store="+str(number)
        # print(page_url)
    
        driver.get(page_url)
        soup1 = BeautifulSoup(driver.page_source, "lxml")
        if "Invalid Link!!!" in soup1.text:
            continue
        location_name = soup1.find("span",{"class":"store-form-head"}).text.strip()
        store_number = location_name.split(" ")[-1]
        addr = list(soup1.find_all("div",{"class":"loc-list"})[0].stripped_strings)
        street_address = " ".join(addr[:-2])
        if "," in addr[-2]:
            city = addr[-2].split(",")[0].replace("\n","").replace("\t","").strip()
            state = addr[-2].split(",")[1].split(" ")[1]
            zipp = addr[-2].split(",")[1].split(" ")[2]
        else:
            city = addr[-2].split(" ")[0].replace("\n","").replace("\t","").strip()
            state = "<MISSING>"
            zipp = addr[-2].split(" ")[-1]
        phone = soup1.find('span', {'class':'store-phone'}).text
        hours =   " ".join(list(soup1.find_all("div",{"class":"loc-list"})[1].stripped_strings))
        
        store = []
        store.append(base_url)
        store.append(location_name)
        store.append(street_address)
        store.append(city)
        store.append(state)
        store.append(zipp)
        store.append("US")
        store.append(store_number)
        store.append(phone)
        store.append("<MISSING>")
        store.append("<MISSING>")
        store.append("<MISSING>")
        store.append(hours)
        store.append(page_url)
        
        for i in range(len(store)):
            if type(store[i]) == str:
                store[i] = ''.join((c for c in unicodedata.normalize('NFD', store[i]) if unicodedata.category(c) != 'Mn'))
        store = [x.replace("–","-") if type(x) == str else x for x in store]
        store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
        # print("data ==="+str(store))
        # print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~````")
        yield store
       
def scrape():
    data = fetch_data()
    write_output(data)


scrape()
