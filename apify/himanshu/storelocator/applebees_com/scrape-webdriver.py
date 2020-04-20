import csv
from bs4 import BeautifulSoup
import requests
from sgrequests import SgRequests
import time
import re
import json
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import platform
system = platform.system()

session = SgRequests()
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
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    driver = get_driver()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
        'accept': '*/*',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
    }
     # it will used in store data.
    addresses = []
    base_url = "https://www.applebees.com/"
    locator_domain = base_url
    location_name = ""
    street_address = ""
    city = ""
    state = ""
    zipp = ""
    country_code = "US"
    store_number = ""
    phone = ""
    location_type = "presidentebarandgrill"
    latitude = ""
    longitude = ""
    raw_address = ""
    hours_of_operation = ""
    driver.get("https://www.applebees.com/en/sitemap")
    soup = BeautifulSoup(driver.page_source,"lxml")
    for link in soup.find("div",class_="site-map").find_all("ul")[8:]:
        for a in link.find_all("a",class_="nav-link"):
            a = "https://www.applebees.com"+a["href"]
            # print(a)
            try:
                driver.get(a)
                time.sleep(3)
                soup1 = BeautifulSoup(driver.page_source,"lxml")
            except Exception as e:
                #print(e)
                continue
            try:
                loc_section = soup1.find("div",{"id":"location-cards-wrapper"})
                
                for loc_block in loc_section.find_all("div",class_="owl-item"):
                    country_code = loc_block.find("input",{"name":"location-country"})["value"]
                    geo_code = loc_block.find("input",{"name":"location-country"}).nextSibling.nextSibling
                    latitude = geo_code["value"].split(",")[0]
                    longitude = geo_code["value"].split(",")[1].split("?")[0]
                    page_url ="https://www.applebees.com"+ loc_block.find("div",class_="map-list-item-header").find("a")["href"]
                    location_name = loc_block.find("div",class_="map-list-item-header").find("span",class_="location-name").text.strip()
                    address = loc_block.find("div",class_="address").find("a",{"title":"Get Directions"})
                    address_list = list(address.stripped_strings)
                    street_address = " ".join(address_list[:-1]).strip()
                    city = address_list[-1].split(",")[0].strip()
                    state = address_list[-1].split(",")[1].split()[0].strip()
                    zipp = address_list[-1].split(",")[1].split()[-1].strip()
                    phone = loc_block.find("a",class_="data-ga phone js-phone-mask").text.strip()
                    store_number= "<MISSING>"
                    driver.get(page_url)
                    time.sleep(3)
                    soup2 = BeautifulSoup(driver.page_source,"lxml")
                    # hours_of_operation = " ".join(list(soup2.find("div",class_="hours").stripped_strings))
                    # print(hours_of_operation)
                    try:
                        hours_of_operation = " ".join(list(soup2.find("div",class_="hours").stripped_strings))
                    except :
                        hours_of_operation = "<MISSING>"
                    store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                    store_number, phone, location_type, latitude, longitude, hours_of_operation,page_url]

                    if str(store[2]) + str(store[-3]) not in addresses:
                        addresses.append(str(store[2]) + str(store[-3]))

                        store = [x if x else "<MISSING>" for x in store]

                        #print("data = " + str(store))
                        #print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
                        yield store
            except:
                continue

            

 
def scrape():
    data = fetch_data()
    write_output(data)


scrape()


