import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
from sgselenium import SgSelenium
import json
import time
from selenium.webdriver.support.wait import WebDriverWait

session = SgRequests()

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
    headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    base_url = "https://annashouseus.com"
    r = session.get("https://annashouseus.com/locations/",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    location_object = {}
    for location in soup.find_all("div",{'class':"vc-location-content"}):
        location_details = list(location.stripped_strings)
        for i in range(len(location_details)):
            if location_details[i] == "Phone:":
                phone = location_details[i+1]
                break
        geo_location = location.find_all("iframe")[-1]["src"]
        if len(geo_location.split("!3d")) != 1:
            location_object[location_details[0]] = [phone,geo_location.split("!3d")[1].split("!")[0],geo_location.split("!2d")[1].split("!")[0]]
        else:
            driver.get("https://annashouseus.com/locations/")
            time.sleep(5)
            driver.find_element_by_xpath("//li[@data-target='" + str(location["id"]) + "']").click()
            driver.switch_to.frame(driver.find_element_by_xpath("//div[@id='" + str(location["id"]) + "']//iframe[@scrolling='no']"))
            time.sleep(3)
            geo_soup = BeautifulSoup(driver.page_source,"lxml")
            for script in geo_soup.find_all("script"):
                if "initEmbed" in script.text:
                    lat = json.loads(script.text.split("initEmbed(")[1].split(");")[0])[21][0][0][2]
                    lng = json.loads(script.text.split("initEmbed(")[1].split(");")[0])[21][0][0][1]
            location_object[location_details[0]] = [phone,lat,lng]
    for location in soup.find_all("div",{"class":"vc-locationContainer"}):
        location_details = list(location.stripped_strings)
        address = location_details[-1].replace("\r","").replace("\n","").replace("\u200e","")
        store = []
        store.append("https://annashouseus.com")
        store.append(location_details[0])
        if len(address.split(",")) == 3:
            store.append(address.split(",")[0])
            store.append(address.split(",")[1])
            store.append(address.split(",")[-1].split(" ")[-2])
            store.append(address.split(",")[-1].split(" ")[-1])
        else:
            store.append(address.split(",")[0])
            store.append(" ".join(address.split(",")[1].split(" ")[1:-1]))
            store.append("<MISSING>")
            store.append(address.split(",")[-1].split(" ")[-1])
        store.append("US")
        store.append("<MISSING>")
        store.append(location_object[location_details[0]][0])
        store.append("<MISSING>")
        store.append(location_object[location_details[0]][1])
        store.append(location_object[location_details[0]][2])
        store.append(soup.find("div",{'class':"et_pb_row et_pb_row_1"}).find("p").text.replace("–","-"))
        store.append("https://annashouseus.com/locations/")
        yield store

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
