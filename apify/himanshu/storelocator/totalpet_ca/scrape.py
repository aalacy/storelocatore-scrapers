import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import requests
# from selenium import webdriver
# from selenium.webdriver.firefox.options import Options
from selenium.webdriver import Firefox
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
# system = platform.system()
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

session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w',encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
   

    driver = get_driver()
    driver.get("http://totalpet.ca/wp-admin/admin-ajax.php?action=store_search&lat=56.130366&lng=-106.346771&max_results=25&search_radius=50&autoload=1")
    
    driver.get("http://totalpet.ca/store-locator/")
    soup1=BeautifulSoup(driver.page_source,'lxml')
    cookies_list = driver.get_cookies()
    cookies_json = {}
    for cookie in cookies_list:
        cookies_json[cookie['name']] = cookie['value']

    cookies_string = str(cookies_json).replace("{", "").replace("}", "").replace("'", "").replace(": ", "=").replace(
        ",", ";")


    url = "http://totalpet.ca/wp-admin/admin-ajax.php?action=store_search&lat=56.130366&lng=-106.34677099999999&max_results=50&search_radius=1000000&autoload=1"

    payload = {}
    headers = {
    'Host': 'totalpet.ca',
    'Referer': 'http://totalpet.ca/store-locator/',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest',
    'Cookie': cookies_string
    }

    data_request = requests.request("GET", url, headers=headers, data = payload)


    base_url = "http://totalpet.ca"
    r = session.get("http://totalpet.ca/store-locator/",headers=headers)
    return_main_object = []
    soup = BeautifulSoup(r.text,"lxml")
    hours_object = {}
    phone_object = {}
    for location in soup.find_all("section",{"itemscope":"itemscope"}):
        location_details = list(location.stripped_strings)
        # print(location_details)
        if len(location_details) < 2:
            continue
        for k in range(len(location_details)):
            if "Store Hours" in location_details[k]:
                hours = " ".join(location_details[k+1:])
                hours_object[location_details[0].lower()] = hours
                phone_object[location_details[0].lower()] = location_details[3]
    data = data_request.json()
    for i in range(len(data)):
        store_data = data[i]
        store = []
        store.append("http://totalpet.ca")
        store.append(store_data["store"])
        store.append(store_data["address"] + store_data["address2"])
        store.append(store_data["city"])
        if store_data["state"]:
            store.append(store_data["state"])
        else:
            store.append("BC")
        store.append(store_data["zip"])
        store.append("CA")
        store.append(store_data["id"])
        store.append(phone_object[store_data["store"].lower()])
        store.append("total pet")
        store.append(store_data['lat'])
        store.append(store_data['lng'])
        store.append(hours_object[store_data["store"].lower()])
        store.append("<MISSING>")
        store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
        # print(store)
        # store = [x.encode('ascii', 'ignore').decode('ascii').strip() if type(x) == str else x for x in store]<- #aa mari line che atyre add kari
        # yield store
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
