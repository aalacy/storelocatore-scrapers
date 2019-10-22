import csv
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import re
import json
import time
from random import randrange
import platform
import time

system = platform.system()

def write_output(data):
    with open('data.csv', mode='w',encoding="utf-8") as output_file:
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
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }
    driver = get_driver()
    driver.get("https://www.anixter.com")
    base_url = "https://www.anixter.com"
    cookies = driver.get_cookies()
    addresses = []
    s = requests.Session()
    for cookie in cookies:
        s.cookies.set(cookie['name'], cookie['value'])
    for country in ["usa","canada"]:
        r = s.get("https://www.anixter.com/bin/locationList?locationPath=/content/anixter/en_us/about-us/contact-us/global-locations-contact-info/" + country,headers=headers)
        for state in r.json():
            state_request = s.get(base_url + state["href"],headers=headers)
            time.sleep(1.2)
            state_soup = BeautifulSoup(state_request.text,"lxml")
            for location in state_soup.find_all("a",{"title":"More Details"}):
                # print(base_url + location["href"])
                location_request = s.get(base_url + location["href"],headers=headers)
                location_soup = BeautifulSoup(location_request.text,"lxml")
                iframe_url = repr(location_soup.find_all("iframe")[-1]["src"]).replace('"',"").replace(r"\r","").replace(r"\n","")
                # print(iframe_url)
                random_number = randrange(5,10)
                time.sleep(random_number)
                if iframe_url[1] == "/":
                    location_details = list(location_soup.find("table").stripped_strings)
                    geo_location = location_soup.find("a",{"title":"Get Directions"})
                    if geo_location:
                        lat = geo_location["href"].split("/")[-1].split(",")[0]
                        lng = geo_location["href"].split("/")[-1].split(",")[1].replace("%0A","")
                else:
                    driver.get(iframe_url)
                    iframe_soup = BeautifulSoup(driver.page_source,"lxml")
                    location_details = list(iframe_soup.find("table").stripped_strings)
                    geo_location = iframe_soup.find_all("iframe")[-1]["src"]
                    lat = geo_location.split("q=")[1].split("%20")[0] if geo_location.split("q=")[1].split("%20")[0] else "<MISSING>"
                    lng = geo_location.split("q=")[1].split("%20")[1].split("&")[0] if geo_location.split("q=")[1].split("%20")[1].split("&")[0] else "<MISSING>"
                if "," not in location_details[2]:
                    location_details[1] = location_details[1] + " " + location_details[2]
                    del location_details[2]
                if re.findall(r"\b[0-9]{5}(?:-[0-9]{4})?\b",location_details[2]) == []:
                    if re.findall("([A-Z]{2})",location_details[2]) == []:
                        location_details[1] = location_details[1] + " " + location_details[2]
                        del location_details[2]
                state_split = re.findall("([A-Z]{2})",location_details[2])
                if state_split:
                    state = state_split[-1]
                else:
                    state = "<MISSING>"
                if country == "usa":
                    store_zip_split = re.findall(r"\b[0-9]{5}(?:-[0-9]{4})?\b",location_details[2])
                    if store_zip_split:
                        store_zip = store_zip_split[-1]
                    else:
                        store_zip = "<MISSING>"
                else:
                    store_zip_split = re.findall(r'[A-Z]{1}[0-9]{1}[A-Z]{1}\s*[0-9]{1}[A-Z]{1}[0-9]{1}',location_details[2])
                    if store_zip_split:
                        store_zip = store_zip_split[-1]
                    else:
                        store_zip = "<MISSING>"
                phone = ""
                for detail in location_details:
                    if re.findall(re.compile(".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"),detail):
                        phone = re.findall(re.compile(".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"),detail)[-1]
                        break
                hours = ""
                for i in range(len(location_details)):
                    if "Operating Hours" in location_details[i]:
                        for j in range(i+1,len(location_details)):
                            if "Solutions" in location_details[j]:
                                break
                            hours = hours + " "  + location_details[j]
                        break
                name = location_soup.find("h1").text.strip()
                store = []
                store.append("https://www.anixter.com")
                store.append(name)
                store.append(location_details[1])
                if store[-1] in addresses:
                    continue
                addresses.append(store[-1])
                store.append(location_details[2].split(",")[0])
                store.append(state)
                store.append(store_zip)
                store.append("US" if country == "usa" else "CA")
                store.append("<MISSING>")
                store.append(phone if phone else "<MISSING>")
                store.append("<MISSING>")
                store.append(lat)
                store.append(lng)
                store.append(hours if hours else "<MISSING>")
                store.append(base_url + location["href"])
                yield store

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
