import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
from sgselenium import SgSelenium
from selenium.webdriver.support.wait import WebDriverWait
import time


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
    driver = SgSelenium().firefox()
    headers = {
        "user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36"
    }
    base_url = "https://www.va.gov"
    r = session.get("https://api.va.gov/v0/facilities/va?address=Test,%20Coffeyville,%20Kansas%2067337,%20United%20States&bbox[]=-1.26265&bbox[]=187.6656&bbox[]=-179.65656&bbox[]=1.55965&type=all&page=1",headers=headers)
    return_main_object = []
    addresses = []
    page_size = r.json()['meta']["pagination"]['total_pages']
    for i in range(1,int(page_size) + 1):
        page_request = session.get("https://api.va.gov/v0/facilities/va?address=Test,%20Coffeyville,%20Kansas%2067337,%20United%20States&bbox[]=-1.26265&bbox[]=187.6656&bbox[]=-179.65656&bbox[]=1.55965&type=all&page="+ str(i),headers=headers)
        for store_data in page_request.json()["data"]:
            location_url = "https://www.va.gov/find-locations/facility/" + store_data["id"]
            if "address_1" not in store_data["attributes"]["address"]["physical"]:
                continue
            address = ""
            if "address_1" in store_data["attributes"]["address"]["physical"] and store_data["attributes"]["address"]["physical"]["address_1"] != None:
                address = address + " " + store_data["attributes"]["address"]["physical"]["address_1"]
            if "address_2" in store_data["attributes"]["address"]["physical"] and store_data["attributes"]["address"]["physical"]["address_2"] != None:
                address = address + " " + store_data["attributes"]["address"]["physical"]["address_2"]
            if "address_3" in store_data["attributes"]["address"]["physical"] and store_data["attributes"]["address"]["physical"]["address_3"] != None:
                address = address + " " + store_data["attributes"]["address"]["physical"]["address_3"]
            store = []
            store.append("https://www.va.gov")
            store.append(store_data["attributes"]["name"])
            store.append(address.replace("<Null>",""))
            if store[-1] in addresses:
                continue
            addresses.append(store[-1])
            store.append(store_data["attributes"]["address"]["physical"]["city"])
            store.append(store_data["attributes"]["address"]["physical"]["state"])
            store.append(store_data["attributes"]["address"]["physical"]["zip"] if store_data["attributes"]["address"]["physical"]["zip"] != "" and store_data["attributes"]["address"]["physical"]["zip"] != None else "<MISSING>")
            store.append("US")
            store.append("<MISSING>")
            store.append(store_data["attributes"]["phone"]["main"].split(" ")[0].split("/")[0] if store_data["attributes"]["phone"]["main"] != None and store_data["attributes"]["phone"]["main"] != "" else "<MISSING>")
            store.append("<MISSING>")
            store.append(store_data["attributes"]["lat"])
            store.append(store_data["attributes"]["long"])
            try:
                driver.get(location_url)
                element = WebDriverWait(driver, 10).until(lambda x: x.find_element_by_xpath("//h4[contains(text(), 'Hours of Operation')]"))
                location_soup = BeautifulSoup(driver.page_source,"lxml")
                hours = " ".join(list(location_soup.find("h4",text=re.compile("Hours of Operation")).parent.stripped_strings))
            except:
                hours = ""
                for key in store_data["attributes"]["hours"]:
                    if store_data["attributes"]["hours"][key] == None:
                        hours = hours + " " + key + " N/A - N/A" 
                    else:
                        hours = hours + " " + key + " " + store_data["attributes"]["hours"][key]
                if hours.count("24/7") == 7:
                    hours = hours.replace("24/7","N/A - N/A")
            store.append(hours.split("In addition")[0] if hours != "" else "<MISSING>")
            store.append(location_url)
            if hours.count("Closed") > 6:
                continue
            yield store

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
