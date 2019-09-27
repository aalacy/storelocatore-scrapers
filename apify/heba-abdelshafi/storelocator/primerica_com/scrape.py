from selenium import webdriver
from time import sleep
import pandas as pd
import re

from selenium.webdriver.chrome.options import Options
options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument("user-agent= 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'")
#driver=webdriver.Chrome('C:\chromedriver.exe', options=options)
driver = webdriver.Chrome("chromedriver", options=options)


def write_output(data):
    df=pd.DataFrame(data)
    df.to_csv('data.csv', index=False)


def fetch_data():
    data={'locator_domain':[],'location_name':[],'street_address':[],'city':[], 'state':[], 'zip':[], 'country_code':[], 'store_number':[],'phone':[], 'location_type':[], 'latitude':[], 'longitude':[], 'hours_of_operation':[]}
    driver.get('http://www.primerica.com/public/locations.html')
    driver.get('http://www.primerica.com/public/locations.html')
    
    status_urls=[i.get_attribute('href') for i in driver.find_elements_by_xpath('//section[@class="content locList"]//li/a')]
    
    zip_urls=[]
    for s_url in status_urls[0:2]:
        driver.get(s_url)
        for i in driver.find_elements_by_xpath('//ul[@class="zip-list"]/li/a'):
            zip_urls.append(i.get_attribute('href'))
    
    sub_data={'zip_urls':[],'locations_data_urls':[]}
        
    for i in zip_urls:
        driver.get(i)
        for i in driver.find_elements_by_xpath('//ul[@class="agent-list"]/li/a'):
            sub_data['locations_data_urls'].append(i.get_attribute('href'))
            sub_data['zip_urls'].append(i)
        


    driver.close()
    return data


def scrape():
    data = fetch_data()
    write_output(data)
scrape()
