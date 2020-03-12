import csv
from bs4 import BeautifulSoup
import re
import json
import ssl
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import time
from selenium.webdriver.support.wait import WebDriverWait
import platform

system = platform.system()
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
    driver = get_driver()
    driver.get("https://www.godandy.com/contact_us.cfm?Page=Contact%20Us")
    base_url = "https://www.godandy.com/"

    soup = BeautifulSoup(driver.page_source, "lxml")
    # print(soup)

    for number in soup.find("select",{"name":"Store"}).find_all("option"):
        store_number = number['value'].split(" ")[-1]
        if store_number == "":
            continue
        try:
            page_url = "https://www.godandy.com/store_details.cfm?Store="+str(store_number.replace("107","6"))
            # print(page_url)
        
            driver.get(page_url)
            soup1 = BeautifulSoup(driver.page_source, "lxml")
            location_name = soup1.find("span",{"class":"store-form-head"}).text.strip()
            addr = list(soup1.find_all("div",{"class":"loc-list"})[0].stripped_strings)
            street_address = " ".join(addr[:-2])
            city = addr[-2].split(",")[0].replace("\n","").replace("\t","").strip()
            state = addr[-2].split(",")[1].split(" ")[1]
            zipp = addr[-2].split(",")[1].split(" ")[2]
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
            # print("data ==="+str(store))
            # print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~````")
            yield store

        except:
            continue
       



   
    

def scrape():
    data = fetch_data()
    write_output(data)


scrape()
