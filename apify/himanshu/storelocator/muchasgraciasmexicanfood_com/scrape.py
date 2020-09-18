import csv
from sgselenium import SgSelenium
from bs4 import BeautifulSoup
import re
import json
import time

def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():

    base_url = "https://www.muchasgraciasmexicanfood.com/locations/"

    driver = SgSelenium().chrome()
    time.sleep(2)

    driver.get(base_url)
    time.sleep(8)

    base = BeautifulSoup(driver.page_source,"lxml")

    return_main_object = []

    items = base.find_all(class_="item")

    for i, location_soup in enumerate(items):
        location_name = location_soup.find(class_="p-title").text.strip()
        addr = location_soup.find(class_="p-area").text.replace("  ",",").strip().split(",")
        street_address = addr[0].strip()
        city = addr[1].strip()
        state = addr[2].strip()
        zipp = addr[3].strip()
        # if len(addr.split(",")) == 2:
        #     street_address = " ".join(addr.split(",")[0].split(" ")[:-1]).replace("Grants","").strip()
        #     city = addr.split(",")[0].split(" ")[-1].replace("Pass","Grants Pass")
        #     state = addr.split(",")[1].split(" ")[1]
        #     zipp = addr.split(",")[1].split(" ")[2]
        # else:
        #     street_address = addr.split(",")[0]
        #     city = addr.split(",")[1]
        #     if len(addr.split(",")[-1].split(" ")) == 2:
        #         state = addr.split(",")[-1].split(" ")[1]
        #         zipp = "<MISSING>"
        #     else:
        #         state = addr.split(",")[-1].split(" ")[1]
        #         zipp = addr.split(",")[-1].split(" ")[2]
        
        try:
            phone = re.findall("\([\d]{3}\) [\d]{3}-[\d]{4}", location_soup.text)[0]
        except:
            phone = "<MISSING>"
        
        days = ""
        hours = ""
        ps = location_soup.find_all(class_="p-area")
        for p in ps:
            if "mon," in p.text.lower():
                days = p.text
            if ":00 " in p.text.lower():
                hours = p.text.strip()

        if days and hours:
            hours_of_operation = hours + days
        else:
            hours_of_operation = "<MISSING>"

        driver.find_elements_by_class_name("item")[i].click()
        time.sleep(2)
        try:
            raw_gps = driver.find_element_by_xpath("//*[(@title='Open this area in Google Maps (opens a new window)')]").get_attribute("href")
            latitude = raw_gps[raw_gps.find("=")+1:raw_gps.find(",")].strip()
            longitude = raw_gps[raw_gps.find(",")+1:raw_gps.find("&")].strip()
        except:
            latitude = "<MISSING>"
            longitude = "<MISSING>"

        store = []
        store.append("muchasgraciasmexicanfood.com")
        store.append(location_name)
        store.append(street_address)
        store.append(city)
        store.append(state)
        store.append(zipp)
        store.append("US")
        store.append("<MISSING>")
        store.append(phone)
        store.append("<MISSING>")
        store.append(latitude)
        store.append(longitude)
        store.append(hours_of_operation)
        store.append(base_url)
        return_main_object.append(store)
    driver.close()
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
