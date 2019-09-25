import csv
import requests
from bs4 import BeautifulSoup
import re
import json
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)
def get_driver():
    options = Options() 
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    return  webdriver.Chrome(ChromeDriverManager().install(),options=options)
def fetch_data():
    base_url = "https://www.liquordepot.ca"
    isFinish=True   
    driver = get_driver()
    driver.get(base_url+"/Our-Stores") 
    while isFinish:
        soup2=BeautifulSoup(driver.page_source,'lxml')
        main2=soup2.find('span',{"id":"dnn_ctr440_View_StoreLocatorGoogleMaps_dlStoreList"}).find_all('span',{'class':"store"})
        for tag in main2:
            storeno=tag.find('a')['href'].split('/')[-1].strip()
            name=tag.find('h3',{'class':"mobile"}).text.strip()
            addr=list(tag.find('div',{'class':"store-address"}).stripped_strings)
            phone=addr[-1].replace('Phone:','').strip()
            del addr[-1]
            st=addr[-1].split(',')
            city=st[0].strip()
            state=st[1].strip()
            zip=st[2].strip()
            del addr[-1]
            address=' '.join(addr).strip()
            hour=' '.join(tag.find('div',{'class':"storeDetails"}).find('table').stripped_strings)
            store=[]
            lt=tag.find('a',text=re.compile('See Map'))['href'].split('@')[1].split(',')
            lat=lt[0]
            lng=lt[1]
            store.append(base_url)
            store.append(name)
            store.append(address)
            store.append(city)
            store.append(state)
            store.append(zip)
            store.append("CA")
            store.append(storeno)
            store.append(phone)
            store.append("liquordepot")
            store.append(lat)
            store.append(lng)
            store.append(hour)
            yield store
        if soup2.find('a',{"id":"dnn_ctr440_View_StoreLocatorGoogleMaps_lnkBottomNextPage"})==None:
            isFinish=False
            continue
        driver.find_element_by_xpath("//a[@id='dnn_ctr440_View_StoreLocatorGoogleMaps_lnkBottomNextPage']").click()
        time.sleep(3)

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
