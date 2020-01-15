from selenium import webdriver
from time import sleep
import pandas as pd
import re

from selenium.webdriver.chrome.options import Options
options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
#options.add_argument('--disable-dev-shm-usage')
#options.add_argument("user-agent= 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'")
driver = webdriver.Chrome("chromedriver", options=options)

#driver=webdriver.Chrome('C:\webdrivers\chromedriver.exe')#, options=options)


def write_output(data):
    df=pd.DataFrame(data)
    df.to_csv('data.csv', index=False)


def fetch_data():

    data={'locator_domain':[],'location_name':[],'street_address':[],'city':[], 'state':[], 'zip':[], 'country_code':[], 'store_number':[],'phone':[], 'location_type':[], 'latitude':[], 'longitude':[], 'hours_of_operation':[],'page_url':[]}
    driver.get('https://www.lowes.ca/stores')
    driver.execute_script("arguments[0].click();",driver.find_element_by_xpath('//button[@class="btn btn-primary btn-block"]'))
    sleep(3)
    
    data['location_name']=[i.text for i in driver.find_elements_by_xpath('//div[@class="col-7"]/p[@class="store-title"]/a')]
    cities_url=[i.get_attribute('href') for i in driver.find_elements_by_xpath('//div[@class="col-7"]/p[@class="store-title"]/a')]
            
    for store in cities_url:
        driver.get(store)                    
        try:
            driver.find_element_by_xpath('//span[@aria-hidden="true"]').click()
        except:
            pass
        
        
        sleep(5)
        store_location=driver.find_element_by_xpath('//div[@class="address"]').text
        store_dir=driver.find_element_by_xpath('//a[@class="btn btn-info btn-sm"][2]').get_attribute('href')
        
        data['hours_of_operation'].append(re.sub(r'([a-zA-Z]+)([1-9]+)',r'\1 \2',driver.find_element_by_xpath('//ul[@class="list list-space-sm"]').text))
        data['page_url'].append(store)
        data['locator_domain'].append('https://www.lowes.ca/stores')       
        data['street_address'].append(store_location.split('\n')[0])
        data['city'].append(store_location.split('\n')[1].split(',')[0])
        data['state'].append(store_location.split('\n')[1].split(',')[1].split()[0])
        data['zip'].append(store_location.split(',')[-1].split('\n')[0].split('CA')[0])
        data['country_code'].append(store_location.split(',')[-1].split('\n')[0].split()[-1])
        data['store_number'].append(store.split('-')[-1])
        data['phone'].append(store_location.split('\n')[2].split(':')[-1])
        data['location_type'].append('Store')        
        data['longitude'].append(store_dir.split('=')[-1].split(',')[1])
        data['latitude'].append(store_dir.split('=')[-1].split(',')[0])
        
    driver.close()
    return data


def scrape():
    data = fetch_data()
    write_output(data)
scrape()
