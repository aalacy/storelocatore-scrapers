import csv
import requests
from bs4 import BeautifulSoup
import re
import json
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import time
import platform
import time

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
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }
    addresses = []
    base_url = "https://www.lelabofragrances.com"
    driver.get('https://www.lelabofragrances.com/front/app/store/search')
    driver.find_element_by_xpath("//button[@class='fs-dropdown-selected']").click()
    driver.find_element_by_xpath("//button[@data-value='EN']").click()
    driver.find_element_by_xpath("//input[@type='text']").click()
    driver.find_element_by_xpath("//div[@data-value='US']").click()
    driver.find_element_by_css_selector(".form-btn.gatracking").click()
    driver.find_element_by_xpath("//button[@id='storeSearch.country-dropdown-selected']").click()
    time.sleep(2)
    driver.find_element_by_xpath("//div[@id='storeSearch.country-dropdown']//button[@data-value='US']").click()
    soup = BeautifulSoup(driver.page_source, "lxml")
    for script in soup.find_all("script"):
        if "storeObjects.push(" in script.text:
            for location in script.text.split("storeObjects.push(")[1:]:
                name = location.split("name")[1].split("',")[0].replace("'","").replace(":","").replace("\\","")
                address1 = location.split("address1")[1].split("',")[0].replace("'","").replace(":","")
                address2 = location.split("address2")[1].split("',")[0].replace("'","").replace(":","")
                street_address = address1 + " " + address2
                city = location.split("city")[1].split("',")[0].replace("'","").replace(":","")
                state = location.split("state")[1].split("',")[0].replace("'","").replace(":","")
                store_zip = location.split("zip")[1].split("',")[0].replace("'","").replace(":","")
                store_id = location.split("id")[1].split("',")[0].replace("'","").replace(":","")
                phone = location.split("phone")[1].split("',")[0].replace("'","").replace(":","")
                lat = location.split("latitude")[1].split("',")[0].replace("'","").replace(":","")
                lng = location.split("longitude")[1].split("',")[0].replace("'","").replace(":","")
                hours = location.split("hours")[1].split("',")[0].replace("'","").replace(":","").replace("<br>"," ").replace("<BR>"," ").strip()
                store = []
                store.append("https://www.lelabofragrances.com")
                store.append(name if name else "<MISSING>")
                store.append(street_address if street_address else "<MISSING>")
                store.append(city if city else "<MISSING>")
                store.append(state if state else "<MISSING>")
                store.append(store_zip if store_zip else "<MISSING>")
                store.append("US")
                store.append(store_id if store_id else "<MISSING>")
                store.append(phone if phone else "<MISSING>")
                store.append("<MISSING>")
                store.append(lat)
                store.append(lng)
                store.append(hours if hours else "<MISSING>")
                store.append("https://www.lelabofragrances.com/front/app/store/search?execution=e1s1")
                store = [x.encode('ascii', 'ignore').decode('ascii').strip() if type(x) == str else x for x in store]
                yield store
    driver.find_element_by_xpath("//button[@id='storeSearch.country-dropdown-selected']").click()
    driver.find_element_by_xpath("//button[@data-value='CANADA']").click()
    soup = BeautifulSoup(driver.page_source, "lxml")
    for script in soup.find_all("script"):
        if "storeObjects.push(" in script.text:
            for location in script.text.split("storeObjects.push(")[1:]:
                name = location.split("name")[1].split("',")[0].replace("'","").replace(":","").replace("\\","")
                address1 = location.split("address1")[1].split("',")[0].replace("'","").replace(":","")
                address2 = location.split("address2")[1].split("',")[0].replace("'","").replace(":","")
                street_address = address1 + " " + address2
                city = location.split("city")[1].split("',")[0].replace("'","").replace(":","")
                state = location.split("state")[1].split("',")[0].replace("'","").replace(":","")
                store_zip = location.split("zip")[1].split("',")[0].replace("'","").replace(":","")
                store_id = location.split("id")[1].split("',")[0].replace("'","").replace(":","")
                phone = location.split("phone")[1].split("',")[0].replace("'","").replace(":","")
                lat = location.split("latitude")[1].split("',")[0].replace("'","").replace(":","")
                lng = location.split("longitude")[1].split("',")[0].replace("'","").replace(":","")
                hours = location.split("hours")[1].split("',")[0].replace("'","").replace(":","").replace("<br>"," ").replace("<BR>"," ").strip()
                store = []
                store.append("https://www.lelabofragrances.com")
                store.append(name if name else "<MISSING>")
                store.append(street_address if street_address else "<MISSING>")
                store.append(city if city else "<MISSING>")
                store.append(state if state else "<MISSING>")
                store.append(store_zip if store_zip else "<MISSING>")
                store.append("CA")
                store.append(store_id if store_id else "<MISSING>")
                store.append(phone if phone else "<MISSING>")
                store.append("<MISSING>")
                store.append(lat)
                store.append(lng)
                store.append(hours if hours else "<MISSING>")
                store.append("https://www.lelabofragrances.com/front/app/store/search?execution=e1s1")
                store = [x.encode('ascii', 'ignore').decode('ascii').strip() if type(x) == str else x for x in store]
                yield store

def scrape():
    data = fetch_data()
    write_output(data)

scrape()