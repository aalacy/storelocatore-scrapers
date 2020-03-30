import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import time
import platform


session = SgRequests()

system = platform.system()

def write_output(data):
    with open('data.csv', mode='w',encoding="utf-8") as output_file:
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
    driver.get("https://www.districttaco.com/pages/locations")
    driver.find_element_by_xpath("//button[@id='ListView']").click()
    time.sleep(5)
    soup = BeautifulSoup(driver.page_source,"lxml")
    geo_locations = []
    location_list = []
    geo_object = {}
    for script in soup.find_all("script"):
        if "function initMap() {" in script.text:
            geo = script.text.split("lat: ")[1:]
            for lat in geo:
                geo_locations.append([lat.split(",")[0],lat.split("lng: ")[1].split("}")[0]])
        if "openingHours" in script.text:
            location_list = json.loads(script.text)["location"]
    for store_data in location_list:
        geo_object[store_data["address"]["streetAddress"]] = geo_locations[0]
        del geo_locations[0]
    for location in soup.find_all("div",{"class":"grid__item medium-up--one-third"}):
        name = location.find("strong").text
        address  = list(location.find("span").stripped_strings)
        if location.find("a",{"href":re.compile("tel:")}):
            phone = location.find("a",{"href":re.compile("tel:")}).text
        else:
            phone = "<MISSING>"
        hours = " ".join(list(location.find("table").stripped_strings))
        zip_split =  re.findall(r"\b[0-9]{5}(?:-[0-9]{4})?\b",address[1])
        store_zip = zip_split[0]
        state_split = re.findall("([A-Z]{2})",address[1])
        if state_split:
            state = state_split[-1]
        else:
            state = "<MISSING>"
        store = []
        store.append("https://www.districttaco.com")
        store.append(name)
        store.append(address[0])
        store.append(address[1].split(",")[0])
        store.append(state)
        store.append(store_zip)
        store.append("US")
        store.append("<MISSING>")
        store.append(phone.strip().replace("  ","") if phone else "<MISSING>")
        store.append("<MISSING>")
        if store[2] in geo_object:
            store.append(geo_object[store[2]][0])
            store.append(geo_object[store[2]][1])
        else:
            for key in geo_object:
                str1 = key
                str2 = store[2]
                str1_words = set(str1.split())
                str2_words = set(str2.split())
                common = str1_words & str2_words
                if len(common) > 1:
                    store.append(geo_object[key][0])
                    store.append(geo_object[key][1])
                    break
        store.append(hours)
        store.append("https://www.districttaco.com/pages/locations")
        yield store
    # hours_object = {}
    # for location in soup.find_all("div",{"class":"grid__item medium-up--one-third"}):
    #     address  = list(location.find("span").stripped_strings)
    #     name = location.find("strong").text.strip()
    #     hours_object[name] = ["-".join(address),hours]
    # headers = {
    # 'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    # }
    # base_url = "https://www.districttaco.com"
    # r = session.get("https://www.districttaco.com/pages/locations",headers=headers)
    # soup = BeautifulSoup(r.text,"lxml")
    # return_main_object = []
    # geo_locations = []
    # for i in range(len(location_list)):
    #     store_data = location_list[i]
    #     store = []
    #     store.append("https://www.districttaco.com")
    #     store.append(store_data["name"])
    #     print(store_data["name"])
    #     for key in hours_object:
    #         if store[1].replace(" District Taco ","") in key:
    #             store.append("-".join(hours_object[key][0].split("-")[:-1]))
    #             break
    #     if len(store) == 2:
    #         for key in hours_object:
    #             if store_data["address"]["addressLocality"] in hours_object[key][0]:
    #                 store.append("-".join(hours_object[key][0].split("-")[:-1]))
    #                 break
    #     store.append(store_data["address"]["addressLocality"])
    #     store.append(store_data["address"]["addressRegion"])
    #     store.append(store_data["address"]["postalCode"])
    #     store.append("US")
    #     store.append("<MISSING>")
    #     store.append(store_data["telephone"])
    #     store.append("<MISSING>")
    #     store.append(geo_locations[i][0])
    #     store.append(geo_locations[i][1])
    #     for key in hours_object:
    #         if store[1].replace(" District Taco ","") in key:
    #                 store.append(hours_object[key][1])
    #                 del hours_object[key]
    #                 break
    #     if len(store) == 12:
    #         for key in hours_object:
    #             if store_data["address"]["addressLocality"] in hours_object[key][0]:
    #                 store.append(hours_object[key][1])
    #                 del hours_object[key]
    #                 break
    #     store.append("<MISSING>")
    #     yield store

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
