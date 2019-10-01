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


import requests
from bs4 import BeautifulSoup
s = requests.Session()
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
    'Method': 'GET',
    'Authority': 'https://www.1800packrat.com',
    'Path': '/en/find-store',
    'Scheme': 'https',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-US,en;q=0.9',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'none',
    'upgrade-insecure-requests': '1'
}
s.headers.update(headers)


def write_output(data):
    df=pd.DataFrame(data)
    df.to_csv('data.csv', index=False)


def fetch_data():
    data={'locator_domain':[],'location_name':[],'street_address':[],'city':[], 'state':[], 'zip':[], 'country_code':[], 'store_number':[],'phone':[], 'location_type':[], 'latitude':[], 'longitude':[], 'hours_of_operation':[]}
    
    #first trial
    driver.get('https://www.1800packrat.com/locations')
    location_data_urls=[i.get_attribute('href') for i in driver.find_elements_by_xpath('//ul[@class="location-list__sub"]/li[@class="location-list__item"]/a')]
    
    for url in location_data_urls[0:2]:
        driver.get(url)
        
    
    
    #second trial    
    url = "https://www.1800packrat.com/locations"
    response = s.get(url, headers=headers)
    soup = BeautifulSoup(response.content, "html.parser")
    location_data_urls=[]
    for i in soup.findAll('ul', {'class': 'location-list__sub'}):
        location_data_urls.append(i.find('li',{'class':'location-list__item'}).find('a',{'class':'location-list__city'})['href'])

   
    
    driver.close()
    return data


def scrape():
    data = fetch_data()
    write_output(data)
scrape()
