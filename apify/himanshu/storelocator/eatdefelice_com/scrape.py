import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import re
import io
import json
import platform
import time


session = SgRequests()

system = platform.system()

def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
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
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    base_url = "http://eatdefelice.com/"
    r = session.get("http://eatdefelice.com/locations/",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    hours = " ".join(list(soup.find("span",{"class":'bodytxt'}).stripped_strings))
    phone_object = {}
    for location_list in soup.find_all("td",{'class':"bodytxt"}):
        for location in list(location_list.stripped_strings)[1:]:
            name = " ".join(location.split(" ")[:-1])
            phone = ''.join(i for i in location.split(" ")[-1] if i.isdigit())
            phone_object[phone] = name
    driver = get_driver()
    driver.get("http://eatdefelice.com/locations/")
    driver.switch_to.frame(driver.find_element_by_xpath("//iframe"))
    time.sleep(5)
    link = driver.find_element_by_xpath("//a[text()='View larger map']").get_attribute("href")
    driver.get(link)
    time.sleep(5)
    location_ids = []
    for location in driver.find_elements_by_xpath("//div[@role='listitem']"):
        location_ids.append(location.get_attribute("data-result-index"))
    for location in location_ids:
        driver.find_element_by_xpath("//div[@data-result-index='"+ location + "']").click()
        time.sleep(5)
        geo_location = driver.current_url
        location_soup = BeautifulSoup(driver.page_source,"lxml")
        phone = ""
        if location_soup.find("span",text=re.compile(".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?")):
            phone = location_soup.find("span",text=re.compile(".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?")).text
        address = location_soup.find("img",{"src":"//www.gstatic.com/images/icons/material/system_gm/1x/place_gm_blue_24dp.png"}).parent.parent.find("span",{"class":"widget-pane-link"}).text
        state_split = re.findall("([A-Z]{2})",address)
        if state_split:
            state = state_split[-1]
        else:
            state = "<MISSING>"
        store_zip_split = re.findall(r"\b[0-9]{5}(?:-[0-9]{4})?\b",address)
        if store_zip_split:
            store_zip = store_zip_split[-1]
        else:
            store_zip = "<MISSING>"
        store = []
        store.append("http://eatdefelice.com")
        if ''.join(i for i in phone if i.isdigit()) in phone_object:
            store.append(phone_object[''.join(i for i in phone if i.isdigit())])
        else:
            store.append("<MISSING>")
        store.append(address.split(",")[0])
        store.append(address.split(",")[1])
        store.append(state)
        store.append(store_zip)
        store.append("US")
        store.append("<MISSING>")
        store.append(phone if phone else "<MISSING>")
        store.append("<MISSING>")
        store.append(geo_location.split("!3d")[1].split("!")[0])
        store.append(geo_location.split("!4d")[1].split("!")[0].split("?")[0])
        store.append(hours.replace("–","-"))
        store.append("http://eatdefelice.com/locations/")
        yield store
        driver.find_element_by_xpath("//span[text()='Back to results']").click()
        time.sleep(5)

def scrape():
    data = fetch_data()
    write_output(data)
scrape()
