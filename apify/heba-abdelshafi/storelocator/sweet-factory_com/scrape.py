from selenium import webdriver
from time import sleep
import pandas as pd
import re

from selenium.webdriver.chrome.options import Options
options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
#driver=webdriver.Chrome('C:\webdrivers\chromedriver.exe', options=options)
driver = webdriver.Chrome("chromedriver", options=options)


def write_output(data):
    df=pd.DataFrame(data)
    df.to_csv('data.csv', index=False)
    
def fetch_data():
    data={'locator_domain':[],'location_name':[],'street_address':[],'city':[], 'state':[], 'zip':[], 'country_code':[], 'store_number':[],'phone':[], 'location_type':[], 'latitude':[], 'longitude':[], 'hours_of_operation':[]}
    
    driver.get('https://www.sweetfactory.com/locations')
    
    location_data=[i.text for i in driver.find_elements_by_xpath('//p[@style="white-space:pre-wrap;"]')]    
    for i in location_data:
        if '\n' in i:
            data['locator_domain'].append('https://www.sweetfactory.com/')
            data['location_name'].append(i.split('\n')[0])
            data['street_address'].append(i.split('\n')[1])
            data['city'].append(i.split('\n')[2].split(',')[0])
            data['state'].append(i.split('\n')[2].split(',')[1].split()[0])
            if len(i.split('\n')[2].split(','))==2:
                data['zip'].append(i.split('\n')[2].split(',')[1].split()[-1])
            if len(i.split('\n')[2].split(','))!=2:
                data['zip'].append(i.split('\n')[2].split(',')[-1])
            data['phone'].append(i.split('\n')[3].split(':')[-1])
            data['country_code'].append('US')
            data['store_number'].append('<MISSING>')
            data['location_type'].append('Candy Stores')
            
    location_data_urls=[i.get_attribute('href') for i in driver.find_elements_by_xpath('//p[@style="white-space:pre-wrap;"]/a')]
    for url in location_data_urls:
        driver.get(url)
        sleep(3)
        geo_data=driver.find_element_by_xpath('//div[@class="lightbox-map hidden"]').get_attribute('data-map-state')
        try:
            data['latitude'].append(re.sub(r'([A-Za-z]|"|:|}|{)| ','',geo_data).split(',')[-2])
        except:
            data['latitude'].append('<MISSING>')
        try:
            data['longitude'].append(re.sub(r'([A-Za-z]|"|:|}|{)| ','',geo_data).split(',')[-1])
        except:
            data['longitude'].append('<MISSING>')
        try:
            data['hours_of_operation'].append(driver.find_element_by_xpath('//strong[@class="u-space-r-half"]').text)
        except:
            data['hours_of_operation'].append('<MISSING>')            
    driver.close()
    return data
    

def scrape():
    data = fetch_data()
    write_output(data)
scrape()