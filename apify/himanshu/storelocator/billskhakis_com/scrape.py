import csv
import requests
from bs4 import BeautifulSoup
import re
import json
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.wait import WebDriverWait
import time
import platform

system = platform.system()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
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
    driver.get("https://www.billskhakis.com/store-locator/search?distance=5000&near=11756&p=1")
    element = WebDriverWait(driver, 5).until(lambda x: x.find_element_by_xpath("//a[@title='No Thanks']"))
    time.sleep(2)
    driver.find_element_by_xpath("//a[@title='No Thanks']").click()
    soup = BeautifulSoup(driver.page_source,"lxml")
    count = int(soup.find("a",{'class':"last"}).text.strip())
    for i in range(1,count + 1):
        geo_object = []
        # print("https://www.billskhakis.com/store-locator/search?distance=5000&near=11756&p=" + str(i))
        while True:
            try:
                driver.get("https://www.billskhakis.com/store-locator/search?distance=5000&near=11756&p=" + str(i))
                time.sleep(2)
                temp_soup = BeautifulSoup(driver.page_source,"lxml")
                time.sleep(2)
                # print("https://www.billskhakis.com/store-locator/" + temp_soup.find_all("script",src=re.compile("_,"))[-1]["src"])
                geo_request = requests.get("https://www.billskhakis.com/store-locator/" + temp_soup.find_all("script",src=re.compile("_,"))[-1]["src"])
                for geo_details in geo_request.text.split("createMarker(")[1:]:
                    lat = geo_details.split("lat:")[1].split(",")[0].replace('"',"")
                    lng = geo_details.split("lng:")[1].split(",")[0].replace('"',"")
                    geo_object.append([lat,lng])
                if geo_object != []:
                    break
            except:
                continue
        element = WebDriverWait(driver, 10).until(lambda x: x.find_element_by_xpath("//div[@class='title']"))
        time.sleep(5)
        for button in driver.find_elements_by_xpath("//div[@class='title']"):
            button.click()
            time.sleep(2)
            location_soup = BeautifulSoup(driver.page_source, "lxml")
            if location_soup.find("div",{'class':"marker-title"}):
                pass
            else:
                time.sleep(6)
                driver.find_element_by_xpath("//button[@title='Zoom in']").click()
                time.sleep(4)
                driver.find_element_by_xpath("//button[@title='Zoom in']").click()
                time.sleep(4)
                location_soup = BeautifulSoup(driver.page_source, "lxml")
            name = location_soup.find("div",{'class':"marker-title"}).text.strip()
            address = location_soup.find("div",{'class':"marker-address"}).text.strip()
            if location_soup.find("div",{'class':"marker-phone"}):
                phone = location_soup.find("div",{'class':"marker-phone"}).text.strip()
            else:
                phone = "<MISSING>"
            if len(address.split(",")) > 2:
                city = address.split(",")[-2]
            elif "." in address:
                city = address.split(".")[1].split(" ")[1]
            else:
                city = address.split(",")[0].split(" ")[1]
            store_zip_split = re.findall("([0-9]{5})",address)
            if store_zip_split:
                store_zip = store_zip_split[-1]
                if address.split(" ")[0] == store_zip:
                    store_zip = "<MISSING>"
            else:
                store_zip = "<MISSING>"
            state_split = re.findall("([A-Z]{2})",address)
            if state_split:
                state = state_split[-1]
            if "21204" in store_zip:
                state = "MD"
                address = "824 Kenilworth Drive"
            if "76710" in store_zip:
                address = "3424 Austin Ave"
                state = "TX"
            store = []
            store.append("https://www.billskhakis.com")
            store.append(name)
            store.append(address.replace(state,"").replace(store_zip,"").replace(city,"").replace(",","").replace("     ","").replace("  ","").replace("TUSCOOSA",""))
            store.append(city.strip())
            store.append(state)
            store.append(store_zip)
            store.append("US")
            store.append("<MISSING>")
            store.append(phone if phone else "<MISSING>")
            store.append("<MISSING>")
            store.append(geo_object[0][0])
            store.append(geo_object[0][0])
            del geo_object[0]
            store.append("<MISSING>")
            store.append("https://www.billskhakis.com/store-locator/search?distance=5000&near=11756&p=" + str(i))
            # print(store)
            yield store

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
