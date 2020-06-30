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
    with open('data.csv', mode='w',encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)
def request_wrapper(url,method,headers,data=None):
   request_counter = 0
   if method == "get":
       while True:
           try:
               r = requests.get(url,headers=headers)
               return r
               break
           except:
               time.sleep(2)
               request_counter = request_counter + 1
               if request_counter > 10:
                   return None
                   break
   elif method == "post":
       while True:
           try:
               if data:
                   r = requests.post(url,headers=headers,data=data)
               else:
                   r = requests.post(url,headers=headers)
               return r
               break
           except:
               time.sleep(2)
               request_counter = request_counter + 1
               if request_counter > 10:
                   return None
                   break
   else:
       return None

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
driver = get_driver()
def fetch_data():
    address = []
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',}
    base_url = "https://www.midwestvisioncenters.com/"
    location_url = "https://www.midwestvisioncenters.com/wp-admin/admin-ajax.php?action=store_search&lat=46.86471&lng=-96.82629&max_results=25&search_radius=500"
    r = request_wrapper(location_url,"get",headers=headers).json()
    for i in r:
        driver.get(i['url'])
        soup = BeautifulSoup(driver.page_source, "lxml")
        
        store = []
        store.append("https://www.midwestvisioncenters.com")
        store.append("Midwest Vision Centers – "+str(i['store']))
        store.append( list(soup.find("p",{"class":"address"}).stripped_strings)[0])
        store.append(i['city'] if i['city'] else "<MISSING>")
        store.append(i["state"] if i['state'] else "<MISSING>")
        store.append(i["zip"].replace("91776","56201") if i['zip'] else "56258")
        store.append(i["country"] if i['country'] else "<MISSING>")
        store.append(i['id'] if i['id'] else "<MISSING>")
        store.append(soup.find("p",{"class":"phone"}).text.strip())
        store.append("Midwest Vision Centers")
        store.append(i['lat'] if i['lat'] else "<MISSING>")
        store.append(i['lng'] if i['lng'] else "<MISSING>")
        soup = BeautifulSoup(i['hours'],"lxml")
        hours_of_operation = (soup.text)
        store.append(hours_of_operation.replace('day',"day ").replace('PM',"PM ").replace("ClosedSunday","Closed Sunday"))
        store.append(i['url'])
        yield store
def scrape():
    data = fetch_data()
    write_output(data)
scrape()
