from selenium import webdriver
from time import sleep
import pandas as pd
#import re

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
    
'''def parse_geo(url):
    lon = re.findall(r'(--?[\d\.]*)', url)[0]
    lat = re.findall(r'\@(-?[\d\.]*)', url)[0]
    return lat, lon'''
    
def fetch_data():
    data={'locator_domain':[],'location_name':[],'street_address':[],'city':[], 'state':[], 'zip':[], 'country_code':[], 'store_number':[],'phone':[], 'location_type':[], 'latitude':[], 'longitude':[], 'hours_of_operation':[]}

    driver.get('https://locations.searsoptical.com')
    sleep(3)
    
    
    state_stores_url=[i.get_attribute('href') for i in driver.find_elements_by_xpath('//a[@class="c-directory-list-content-item-link"]')]
    number_stores_state=[int(i.text.split('(')[-1].split(')')[0]) for i in driver.find_elements_by_xpath('//span[@class="c-directory-list-content-item-count"]')]
    for ind,i in enumerate(state_stores_url):
        driver.get(i)
        sleep(3)
        if number_stores_state[ind]>1:
            cities_stores=[i.get_attribute('href') for i in driver.find_elements_by_xpath('//a[@class="c-directory-list-content-item-link"]')]
            for j in cities_stores:
                driver.get(j)
                sleep(3)
                
                data['locator_domain'].append('http://searsoptical.com/')
                data['location_name'].append(driver.find_element_by_xpath('//div[@class="location-subheader"]').text)
                data['street_address'].append(driver.find_element_by_xpath('//span[@class="c-address-street c-address-street-1"]').text)
                data['city'].append(driver.find_element_by_xpath('//span[@itemprop="addressLocality"]').text)
                data['state'].append(driver.find_element_by_xpath('//span[@itemprop="addressRegion"]').text)
                data['zip'].append(driver.find_element_by_xpath('//span[@itemprop="postalCode"]').text)
                data['phone'].append(driver.find_element_by_xpath('//div[@class="hidden-xs"]//span[@itemprop="telephone"]').text)
                data['hours_of_operation'].append(driver.find_element_by_css_selector('div.c-hours-today.open-today.closed-now div.c-location-hours-today-details-row.js-day-of-week-row.is-today.js-is-today>div').text)
                data['location_type'].append('<MISSING>')
                data['store_number'].append('<MISSING>')
                data['country_code'].append('US')
                data['latitude'].append('<INACCESSIBLE>')
                data['longitude'].append('<INACCESSIBLE>')
                           
        else:
            data['locator_domain'].append('http://searsoptical.com/')
            data['location_name'].append(driver.find_element_by_xpath('//div[@class="location-subheader"]').text)
            data['street_address'].append(driver.find_element_by_xpath('//span[@class="c-address-street c-address-street-1"]').text)
            data['city'].append(driver.find_element_by_xpath('//span[@itemprop="addressLocality"]').text)
            data['state'].append(driver.find_element_by_xpath('//span[@itemprop="addressRegion"]').text)
            data['zip'].append(driver.find_element_by_xpath('//span[@itemprop="postalCode"]').text)
            data['phone'].append(driver.find_element_by_xpath('//div[@class="hidden-xs"]//span[@itemprop="telephone"]').text)
            data['hours_of_operation'].append(driver.find_element_by_css_selector('div.c-hours-today.open-today.closed-now div.c-location-hours-today-details-row.js-day-of-week-row.is-today.js-is-today>div').text)
            data['location_type'].append('<MISSING>')
            data['store_number'].append('<MISSING>')
            data['country_code'].append('US')
            data['latitude'].append('<INACCESSIBLE>')
            data['longitude'].append('<INACCESSIBLE>')
            
    driver.close()        
    return data


def scrape():
    data = fetch_data()
    write_output(data)
scrape()