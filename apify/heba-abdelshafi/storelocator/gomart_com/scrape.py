from selenium import webdriver
from time import sleep
import pandas as pd
import re

from selenium.webdriver.chrome.options import Options
options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
#driver=webdriver.Chrome('C:\chromedriver.exe', options=options)
driver = webdriver.Chrome("chromedriver", options=options)


def write_output(data):
    df=pd.DataFrame(data)
    df.to_csv('data.csv', index=False)


def fetch_data():
    data={'locator_domain':[],'location_name':[],'street_address':[],'city':[], 'state':[], 'zip':[], 'country_code':[], 'store_number':[],'phone':[], 'location_type':[], 'latitude':[], 'longitude':[], 'hours_of_operation':[]}
    driver.get('https://gomart.com/locations/')
    #first try
    location_data=[i.text for i in driver.find_elements_by_xpath('//li[@class="store"]')]
    
    #second try
    globalvar = driver.execute_script("return window.map.addMarker.toString()")
    

    driver.close()
    return data


def scrape():
    data = fetch_data()
    write_output(data)
scrape()
