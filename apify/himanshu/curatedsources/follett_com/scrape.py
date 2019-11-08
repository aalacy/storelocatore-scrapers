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
    headers = {
        "user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36"
    }
    r = requests.get("https://www.follett.com/bookstores",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    states = []
    addresses = []
    driver = get_driver()
    for state in soup.find("select",{'name':"state"}).find_all("option"):
        if state["value"] in states:
            continue
        states.append(state["value"])
        driver.get("https://www.follett.com/bookstores-search?state="+str(state["value"]))
        state_soup = BeautifulSoup(driver.page_source,"lxml")
        for location in state_soup.find_all("div",{"class":'block-store'}):
            if location.find("h4",text=re.compile("Can't Find Your School?")):
                continue
            url = "https://www.follett.com" + location.find("a")["href"]
            # print(url)
            driver.get(url)
            location_soup = BeautifulSoup(driver.page_source,"lxml")
            name = location_soup.find("h1").text.strip()
            city = " ".join(list(location_soup.find("span",{"itemprop":"addressLocality"}).stripped_strings))
            address = ""
            street_address = " ".join(list(location_soup.find("div",{"itemprop":"address"}).stripped_strings))
            if len(street_address.split(city)) == 2:
                address = street_address.split(city)[0]
            else:
                # print(street_address.split(city))
                address = address + street_address.split(city)[0] + " "
                for add in street_address.split(city)[1:-1]:
                    address = address + city + add 
            state = " ".join(list(location_soup.find("span",{"itemprop":"addressRegion"}).stripped_strings))
            zip = list(location_soup.find("div",{"itemprop":"address"}).stripped_strings)[-1]
            if location_soup.find("span",{"itemprop":"telephone"}):
                phone = location_soup.find("span",{"itemprop":"telephone"}).text.strip()
            else:
                phone = "<MISSING>"
            print(phone)
            if location_soup.find("meta",{"itemprop":"latitude"}):
                lat = location_soup.find("meta",{"itemprop":"latitude"})["content"]
            else:
                lat = "<MISSING>"
            if location_soup.find("meta",{"itemprop":"longitude"}):
                lng = location_soup.find("meta",{"itemprop":"longitude"})["content"]
            else:
                lng = "<MISSING>"
            store = []
            store.append("https://www.follett.com")
            store.append(name)
            store.append(address.replace("  "," "))
            if store[-1] in addresses:
                continue
            addresses.append(store[-1])
            store.append(city)
            store.append(state)
            store.append(zip)
            store.append("US" if zip.replace("-","").replace(" ","").isdigit() else "CA")
            store.append(url.split("storeid=")[1].split("-")[-1])
            store.append(phone if phone else "<MISSING>")
            store.append("<MISSING>")
            store.append(lat)
            store.append(lng)
            store.append("<MISSING>")
            store.append(url)
            # print(store)
            yield store

def scrape():
    data = fetch_data()
    write_output(data)

scrape()