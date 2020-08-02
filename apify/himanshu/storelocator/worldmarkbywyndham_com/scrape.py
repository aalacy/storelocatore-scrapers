import csv
import requests
from bs4 import BeautifulSoup
import re
import json
from sgselenium import SgSelenium
from selenium.webdriver.support.wait import WebDriverWait
import time
import unicodedata

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }
    driver = SgSelenium().firefox()
    addresses =[]
    base_url= "https://www.worldmarkbywyndham.com/resorts/index.html"
    driver.get(base_url)
    soup= BeautifulSoup(driver.page_source,"lxml")
    cities = []
    for button in driver.find_elements_by_xpath("//select[@name='parent_selection']/option"):
        state = button.get_attribute("value")
        # if state == 'British Columbia':
        #     country_code='CA'
        # else:
        #     country_code='US'
        # print(country_code)
        # if len(state) != 2:
        #     continue
        if state:
            cities.append(state)
            # print(cities) 
            # print(state)

    for state in cities:
        # driver.find_element_by_xpath("//select[@name='parent_selection']").click()
        driver.find_element_by_xpath("//option[@value='" + state + "']").click()
        # driver.find_elements_by_xpath("//select[@name='parent_selection']").click()

        time.sleep(2)
        list_a = []
        list_a1 = []

        for a_tag in driver.find_elements_by_xpath("//select[@name='child_selection']/option"):
            list_a.append(a_tag.text)
            # list_a.append(a_tag.get_attribute("value"))
            list_a1.append(a_tag.get_attribute("value"))
            time.sleep(2)
        for index,data in enumerate(list_a):
            pk=(list_a1[index])
            # print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
            # print(data)
            # print(state)

            store = []
            store.append("https://www.worldmarkbywyndham.com/")
            store.append(data if data else "<MISSING>") 
            store.append("<MISSING>")
            store.append("<MISSING>")
            if state == 'Fiji':
                continue
            if  state == 'Mexico':
                continue
            if state =='British Columbia':
                country_code='CA'
            else:
                country_code='US'
            store.append(state if state else "<MISSING>")
            store.append("<MISSING>")           
            store.append(country_code)              
            store.append("<MISSING>") 
            store.append("<MISSING>")
            store.append("RESORT")
            store.append("<MISSING>")
            store.append("<MISSING>")
            store.append("<MISSING>")
            store.append("https://www.worldmarkbywyndham.com/resorts/"+pk)
            yield store
       # print("~~~~~~~~~~~~")    
    driver.quit()
       
    
def scrape():
    data = fetch_data()
    write_output(data)

scrape()
