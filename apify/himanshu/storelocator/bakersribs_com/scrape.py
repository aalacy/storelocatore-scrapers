import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
from sgselenium import SgSelenium
import time
from selenium.webdriver.support.wait import WebDriverWait

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
    headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    base_url = "http://bakersribs.com"
    addresses = []
    driver = SgSelenium().firefox()
    driver.get("http://bakersribs.com/#locations")
    soup = BeautifulSoup(driver.page_source, "lxml")
    print(driver.page_source)
    return_main_object = []
    locations = soup.find_all("div",{'class':"et_pb_blurb_container"})
    print(locations)
    for location in locations:
        print(location)
        len1 = list(location.stripped_strings)
        if len(len1)!= 1:
            city = location.find("h4").text.replace("Caddo Mills","Greenville") 
            name =location.find("h4").text.strip()
            state =''
            hours1 =''
            phone =''
            st1 = len1[1].replace(", MN Phone:",'')
            state1 = location.text.split("Phone:")[0].replace("\n","").split(",")
            if len(state1)==2:
                state = state1[-1]
            phone_list = re.findall(re.compile(".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"), str(location.text))
            if phone_list:
                phone =  phone_list[-1]
            hours = list(location.stripped_strings)[2:]
            for q in range(len(hours)):
                if "HOURS" ==hours[q]:
                    hours1 = hours[q+1:]
            # print(hours)
            store = []
            store.append("http://bakersribs.com")
            store.append(name)
            store.append(st1.encode('ascii', 'ignore').decode('ascii').strip().replace(", TX",""))
            store.append(city.encode('ascii', 'ignore').decode('ascii').strip())
            store.append(state.encode('ascii', 'ignore').decode('ascii').strip() if state else "<MISSING>")
            store.append("<MISSING>")
            store.append("US")
            store.append("<MISSING>")
            store.append(phone.replace("\xa0","").encode('ascii', 'ignore').decode('ascii').strip())
            store.append("<MISSING>")
            store.append("<MISSING>")
            store.append("<MISSING>")
            store.append(" ".join(hours1).encode('ascii', 'ignore').decode('ascii').strip())
            store.append("<MISSING>")
            yield store

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
