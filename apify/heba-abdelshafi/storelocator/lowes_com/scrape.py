from selenium import webdriver
from time import sleep
import pandas as pd
import itertools

import json

from selenium.webdriver.chrome.options import Options
options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument("user-agent= 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'")
driver = webdriver.Chrome("chromedriver", options=options)

#driver=webdriver.Chrome('C:\webdrivers\chromedriver.exe')#, options=options)


def write_output(data):
    df=pd.DataFrame(data)
    df.to_csv('data.csv', index=False)


def fetch_data():

    data={'locator_domain':[],'location_name':[],'street_address':[],'city':[], 'state':[], 'zip':[], 'country_code':[], 'store_number':[],'phone':[], 'location_type':[], 'latitude':[], 'longitude':[], 'hours_of_operation':[],'page_url':[]}
    driver.get('https://www.lowes.com/Lowes-Stores')
    states_url=[i.get_attribute('href') for i in driver.find_elements_by_xpath('//div[@class="primaryheading"]/following-sibling::div//li[@role="listitem"]/a')]
    
    cities_url=[]
    for url in states_url:
        driver.get(url)
        sleep(3)
        cities_url.append([i.get_attribute('href') for i in driver.find_elements_by_xpath('//div[@class="v-spacing-small"]/span/following-sibling::a')])
    cities_url=list(itertools.chain.from_iterable(cities_url))
        
    for store in cities_url:
        driver.get(store)
        sleep(3)
        data['page_url'].append(store)
        data['locator_domain'].append('https://www.lowes.com/Lowes-Stores')
        data['location_name'].append(driver.find_element_by_xpath('//header[@class="sc-gZMcBi bhmCuk"]/h1[2]').text)
        store_location=driver.find_element_by_xpath('//div[@aria-labelledby="addressSection"]').text
        data['street_address'].append(store_location.split('\n')[0])
        data['city'].append(store_location.split('\n')[1].split(',')[0])
        data['state'].append(store_location.split('\n')[1].split(',')[1].split()[0])
        data['zip'].append(store_location.split('\n')[1].split(',')[1].split()[1])
        data['country_code'].append('US')
        data['store_number'].append(driver.find_element_by_xpath('//span[@aria-hidden="true"][contains(text(),"Store")]').text.split('#')[1])
        data['phone'].append(driver.find_element_by_xpath('//span[@itemprop="telephone"][contains(text(),"Main")]').text.split(':')[1])
        data['location_type'].append(driver.find_element_by_xpath('//h3[@id="storeDescription"]').text.split()[0])        
        data['hours_of_operation'].append(driver.find_element_by_xpath('//div[@aria-labelledby="storeHoursSection"]').text)

        page = driver.page_source
        start = 'window.__PRELOADED_STATE__ = '
        end   = '</script>'
        j = page[page.find(start) + len(start):]
        j = j[:j.find(end)]
        j = json.loads(j)
        
        data['longitude'].append(j['storeDetails']['long'])
        data['latitude'].append(j['storeDetails']['lat'])
        
        
        
    driver.close()
    return data


def scrape():
    data = fetch_data()
    write_output(data)
scrape()
