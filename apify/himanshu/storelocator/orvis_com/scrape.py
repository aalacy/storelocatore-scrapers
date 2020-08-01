import csv
import requests
from bs4 import BeautifulSoup
import re
from sgselenium import SgSelenium
from selenium.webdriver.support.wait import WebDriverWait
import json
import time


def write_output(data):
    with open('data.csv', mode='w',encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    print("start")
    headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    base_url = "https://orvis.com"
    driver = SgSelenium().firefox()
    driver.get("https://stores.orvis.com/")
    WebDriverWait(driver, 25).until(lambda x: x.find_element_by_xpath("//a[@href='https://stores.orvis.com/']"))
    print("start 1")
    time.sleep(10)
    soup = BeautifulSoup(driver.page_source,"lxml")
    return_main_object = []
    geo_object = {}
    addresses = []
    for script in soup.find_all("script"):
        if "regionData" in script.text:
            location_list = script.text.split("regionData:")[1].split("alias:")[1:-1]
            for i in range(len(location_list)):
                state = location_list[i].split("}")[0].replace("'","").replace(" ","")
                # print(state)
                # print("https://stores.orvis.com/" + state)
                driver.get("https://stores.orvis.com/" + state)
                WebDriverWait(driver, 25).until(lambda x: x.find_element_by_xpath("//a[@href='https://stores.orvis.com/']"))
                time.sleep(5)
                state_soup = BeautifulSoup(driver.page_source,"lxml")
                for script1 in state_soup.find_all("script"):
                    if "var contentString =" in script1.text:
                        for geo_location in script1.text.split("var contentString =")[1:]:
                            lat = geo_location.split("google.maps.LatLng(")[1].split(",")[0]
                            lng = geo_location.split("google.maps.LatLng(")[1].split(",")[1].split(")")[0]
                            store_name = (geo_location.split("new google.maps.Marker(")[1].split("});")[0] + "}").split("title:")[1].split("icon")[0].strip().replace('"',"")[:-1]
                            geo_object[store_name] = [lat,lng]
                for location in state_soup.find_all("div",{"class":"OSL-results-column-wrapper"})[1:]:
                    name = location.find("h4",{"class":"margin-bottom-5"}).text
                    # print(name)
                    address = list(location.find("p",{"class":"margin-bottom-10"}).stripped_strings)
                    if location.find("a",text=re.compile(".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?")):
                        phone = location.find("a",text=re.compile(".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?")).text
                    else:
                        phone = "<MISSING>"
                    if location.find("div",{"class":"weekly-hours"}):
                        hours = " ".join(list(location.find("div",{"class":"weekly-hours"}).stripped_strings))
                    elif location.find("div",{"id":"current_week"}):
                        hours = " ".join(list(location.find("div",{"id":"current_week"}).stripped_strings))
                    else:
                        hours = "<MISSING>"
                    store = []
                    store.append("https://orvis.com")
                    store.append(name)
                    store.append(address[0] if len(address) > 1 and "," not in address[0] else "<MISSING>")
                    if store[-1] != "<MISSING>":
                        if store[-1] in addresses:
                            continue
                        addresses.append(store[-1])
                    store.append(address[-1].split(",")[0] if address[-1].split(",")[0] != "" else "<MISSING>")
                    store.append(address[-1].split(",")[1].split(" ")[-2] if address[-1].split(",")[1].split(" ")[-2] != "" else "<MISSING>")
                    store.append(address[-1].split(",")[1].split(" ")[-1] if len(address[-1].split(",")[1].split(" ")[-1]) > 4 else "<MISSING>")
                    if store[-1] == "00000":
                        store[-1] = "<MISSING>"
                    store.append("US")
                    store.append("<MISSING>")
                    store.append(phone if phone else "<MISSING>")
                    if "(" in store[-1] and ")" in store[-1]:
                        if store[-1].split("(")[1].split(")")[0].isdigit() == False:
                            store[-1] = store[-1].split("(")[0]
                    store.append("<MISSING>")
                    for key in geo_object:
                        if key in name:
                            store.append(geo_object[key][0])
                            store.append(geo_object[key][1])
                            del geo_object[key]
                            break
                    if len(store) == 10:
                        store.append("<INACCESSIBLE>")
                        store.append("<INACCESSIBLE>")
                    store.append(hours)
                    store.append("https://stores.orvis.com/" + state)
                    # print(store)
                    yield store

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
