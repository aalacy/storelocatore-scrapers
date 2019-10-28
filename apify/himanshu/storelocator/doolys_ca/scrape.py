import csv
import requests
from bs4 import BeautifulSoup
import re
import json
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.wait import WebDriverWait
import time
import html
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
    r = requests.get("https://www.doolys.ca/locations-1")
    soup = BeautifulSoup(r.text,"lxml")
    iframe_link = soup.find("iframe")["src"]
    r = requests.get(iframe_link)
    soup = BeautifulSoup(r.text,"lxml")
    geo_location = {}
    for script in soup.find_all("script"):
        if "_pageData" in script.text:
            location_list = json.loads(script.text.split('var _pageData = "')[1].split('\n";')[0].replace('\\"','"').replace(r"\n","")[:-2].replace("\\"," "))[1][6] # [0][12][0][13][0]
            for state in location_list:
                locations = state[4]
                for location in locations:
                    geo_location[location[5][0][0].replace(" u0027s","'s")] = location[4][0][1]
    driver = get_driver()
    addresses = []
    driver.get(iframe_link)
    time.sleep(3)
    driver.find_element_by_xpath("//div[@class='i4ewOd-pzNkMb-ornU0b-b0t70b-Bz112c']").click()
    for button in driver.find_elements_by_xpath("//*[contains(text(), '...')]"):
        time.sleep(1)
        button.click()
    for button in driver.find_elements_by_xpath("//div[contains(@index, '')]"):
        try:
            if button.get_attribute("index") == None:
                continue
            time.sleep(1)
            button.click()
            time.sleep(2)
            location_soup = BeautifulSoup(driver.page_source, "lxml")
            name = list(location_soup.find("div",text=re.compile("name")).parent.stripped_strings)[1]
            address = list(location_soup.find("div",text=re.compile("Details from Google Maps")).parent.stripped_strings)[1]
            street_address = address.split(",")[0]
            city = address.split(",")[1]
            store_zip_split = re.findall(r'[A-Z]{1}[0-9]{1}[A-Z]{1}\s*[0-9]{1}[A-Z]{1}[0-9]{1}',address)
            if store_zip_split:
                store_zip = store_zip_split[-1]
            else:
                store_zip = "<MISSING>"
            state_split = re.findall("([A-Z]{2})",address)
            if state_split:
                state = state_split[-1]
            else:
                state = "<MISSING>"
            location_details = list(location_soup.find("div",text=re.compile("description")).parent.stripped_strings)
            for detail in location_details:
                if "Tel" in detail:
                    phone = detail.split("Tel")[1]
            for i in range(len(location_details)):
                if "Hours of Operation" in location_details[i]:
                    hours = " ".join(location_details[i+1:])
                    break
            store = []
            store.append("https://www.doolys.ca")
            store.append(name)
            store.append(street_address)
            store.append(city)
            store.append(state)
            store.append(store_zip)
            store.append("CA")
            store.append("<MISSING>")
            store.append(phone.replace(".:","").replace("\xa0","").replace('& Fax: ',"") if phone else "<MISSING>")
            store.append("<MISSING>")
            store.append(geo_location[name][0])
            store.append(geo_location[name][1])
            store.append(hours.replace("\xa0","") if hours else "<MISSING>")
            store.append('https://www.doolys.ca/locations-1')
            store = [x.encode('ascii', 'ignore').decode('ascii').strip() if type(x) == str else x for x in store]
            yield store
            time.sleep(2)
            driver.find_element_by_xpath("//span[@class='HzV7m-tJHJj-LgbsSe-Bz112c qqvbed-a4fUwd-LgbsSe-Bz112c']").click()
        except Exception as e:
            time.sleep(1)

def scrape():
    data = fetch_data()
    write_output(data)

scrape()