import csv
import requests
from bs4 import BeautifulSoup
import re
import json
from sgselenium import SgSelenium
from selenium.webdriver.firefox.options import Options
import urllib
import html

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    driver = SgSelenium().firefox()
    driver.get("https://www.citgo.com/locator/store-locators/store-locator")
    cookies = driver.get_cookies()
    s = requests.Session()
    for cookie in cookies:
        s.cookies.set(cookie['name'], cookie['value'])
    return_main_object = []
    soup = BeautifulSoup(driver.page_source,"lxml")
    __VIEWSTATE = urllib.parse.quote(soup.find("input",{"name":"__VIEWSTATE"})["value"])
    __CMSCsrfToken = urllib.parse.quote(soup.find("input",{"name":"__CMSCsrfToken"})["value"])
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
        "Referer": "https://www.citgo.com/locator/store-locators/store-locator",
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    }
    data = '__CMSCsrfToken=' + __CMSCsrfToken + '&lng=en-US&store-distance=10&__VIEWSTATE=' + __VIEWSTATE + '&__CALLBACKID=p%24lt%24WebPartZone3%24PageContent%24pageplaceholder%24p%24lt%24WebPartZone3%24Widgets%24StoreLocator&__CALLBACKPARAM=11756%20Spring%20Club%20Drive%2C%20San%20Antonio%2C%20TX%2C%20USA%7C200000'
    r = s.post("https://www.citgo.com/locator/store-locators/store-locator",headers=headers,data=data)
    if r.text[0] == "s":
        location_list = json.loads(r.text[1:])
    else:
        location_list = r.json()
    for store_data in location_list["Locations"]:
        if store_data["country"] not in ("US","CA"):
            continue
        store = []
        store.append("https://www.citgo.com")
        store.append(store_data["name"])
        store.append(store_data["address"])
        store.append(store_data["city"])
        store.append(store_data["state"])
        store.append(store_data["zip"])
        store.append(store_data["country"])
        store.append(store_data["number"])
        store.append(store_data["phone"] if store_data["phone"] else "<MISSING>")
        store.append("<MISSING>")
        store.append(store_data["latitude"])
        store.append(store_data["longitude"])
        hours = ""
        if "hrsmonstart" in store_data and store_data["hrsmonstart"]:
            hours = hours + " mon " + store_data["hrsmonstart"] + " - " + store_data["hrsmonend"]
        if "hrstuesstart" in store_data and store_data["hrstuesstart"]:
            hours = hours + " tues " + store_data["hrstuesstart"] + " - " + store_data["hrstuesend"]
        if "hrswedstart" in store_data and store_data["hrswedstart"]:
            hours = hours + " wed " + store_data["hrswedstart"] + " - " + store_data["hrswedend"]
        if "hrsthursstart" in store_data and store_data["hrsthursstart"]:
            hours = hours + " thurs " + store_data["hrsthursstart"] + " - " + store_data["hrsthursend"]
        if "hrsfristart" in store_data and store_data["hrsfristart"]:
            hours = hours + " fri " + store_data["hrsfristart"] + " - " + store_data["hrsfriend"]
        if "hrssatstart" in store_data and store_data["hrssatstart"]:
            hours = hours + " sat " + store_data["hrssatstart"] + " - " + store_data["hrssatend"]
        if "hrssunstart" in store_data and store_data["hrssunstart"]:
            hours = hours + " sun " + store_data["hrssunstart"] + " - " + store_data["hrssunend"]
        store.append(hours if hours else "<MISSING>")
        if hours.count("CLOSE") == 14:
            continue
        store.append("<MISSING>")
        for i in range(len(store)):
            store[i] = html.unescape(store[i])
        yield store

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
