import csv
import requests
from bs4 import BeautifulSoup
import re
import json
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.wait import WebDriverWait
import time
import unicodedata
import platform
from sgrequests import SgRequests
session = SgRequests()
system = platform.system()

def write_output(data):
    with open('data.csv', mode='w',encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
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
    
    base_url = "https://pizzadepot.ca/"
    driver.get("https://pizzadepot.ca/index")
    soup = BeautifulSoup(driver.page_source, "lxml")
    # ontario location
    for link in soup.find("select",{"id":"locationid"}).find_all("option"):
        url = link['value']
        driver.get(url)
        time.sleep(3)

        soup1 = BeautifulSoup(driver.page_source, "lxml")
        for page in soup1.find_all("a",{"class":"btn-xlg btn-danger btn-block c-btn-uppercase c-btn-bold"}):
            page_url = page['href']
            driver.get(page_url)
            soup2 = BeautifulSoup(driver.page_source, "lxml")
            location_name = soup2.find("div",{"class":"c-contact-title-1"}).find("h3").text.strip()
            street_address = soup2.find_all("span",{"class":"bs-glyphicon-class"})[0].text.split(",")[0].strip()
            # print(street_address)
            try:
                city = soup2.find_all("span",{"class":"bs-glyphicon-class"})[0].text.split(",")[1].strip()
            except:
                city = "<MISSING>"
            state = "ON"
            zipp = soup2.find_all("span",{"class":"bs-glyphicon-class"})[1].text.strip()
            phone = soup2.find_all("span",{"class":"bs-glyphicon-class"})[2].text.strip()
            store_number = page_url.split("/")[-1]
            try:
                coord = soup2.find_all("iframe")[-1]['src']
                latitude = coord.split("!3d")[1].split("!")[0]
                longitude = coord.split("!2d")[1].split("!")[0]
            except:
                latitude = "<MISSING>"
                longitude = "<MISSING>"
            if len(soup2.find_all("p")) == 4:
                hours = " ".join(list(soup2.find_all("p")[-1].stripped_strings))
            else:
                hours = "<MISSING>"

            store = []
            store.append(base_url)
            store.append(location_name if location_name else "<MISSING>") 
            store.append(street_address if street_address else "<MISSING>")
            store.append(city if city else "<MISSING>")
            store.append("ON")
            store.append(zipp if zipp else "<MISSING>")
            store.append("CA")
            store.append(store_number if store_number else"<MISSING>") 
            store.append(phone if phone else "<MISSING>")
            store.append("<MISSING>")
            store.append(latitude if latitude else "<MISSING>")
            store.append(longitude if longitude else "<MISSING>")
            store.append(hours)
            store.append(page_url if page_url else "<MISSING>")
            store = [x.encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
            yield store 
    ### Alberta location

    page_url = "https://pizzadepot.ca/locationDetails/44"
    driver.get(page_url)
    soup3 = BeautifulSoup(driver.page_source, "lxml")
    location_name = soup3.find("div",{"class":"c-contact-title-1"}).find("h3").text.strip()
    street_address = soup3.find_all("span",{"class":"bs-glyphicon-class"})[0].text.split(",")[0].strip()
    try:
        city = soup3.find_all("span",{"class":"bs-glyphicon-class"})[0].text.split(",")[1].strip()
    except:
        city = "<MISSING>"
    state = "ON"
    zipp = soup3.find_all("span",{"class":"bs-glyphicon-class"})[1].text.strip()
    phone = soup3.find_all("span",{"class":"bs-glyphicon-class"})[2].text.strip()
    store_number = page_url.split("/")[-1]
    try:
        coord = soup3.find_all("iframe")[-1]['src']
        latitude = coord.split("!3d")[1].split("!")[0]
        longitude = coord.split("!2d")[1].split("!")[0]
    except:
        latitude = "<MISSING>"
        longitude = "<MISSING>"
    if len(soup3.find_all("p")) == 4:
        hours = " ".join(list(soup3.find_all("p")[-1].stripped_strings))
    else:
        hours = "<MISSING>"

    store = []
    store.append(base_url)
    store.append(location_name if location_name else "<MISSING>") 
    store.append(street_address if street_address else "<MISSING>")
    store.append(city if city else "<MISSING>")
    store.append("AB")
    store.append(zipp if zipp else "<MISSING>")
    store.append("CA")
    store.append(store_number if store_number else"<MISSING>") 
    store.append(phone if phone else "<MISSING>")
    store.append("<MISSING>")
    store.append(latitude if latitude else "<MISSING>")
    store.append(longitude if longitude else "<MISSING>")
    store.append(hours)
    store.append(page_url if page_url else "<MISSING>")
    store = [x.encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
    yield store 
def scrape():
    data = fetch_data()
    write_output(data)
scrape()
