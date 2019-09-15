from selenium import webdriver
from time import sleep
import pandas as pd

def write_output(data):
    df=pd.DataFrame(data)
    df.to_csv('data.csv', index=False)
 
    
def fetch_data():
    data={'locator_domain':[],'location_name':[],'street_address':[],'city':[], 'state':[], 'zip':[], 'country_code':[], 'store_number':[],'phone':[], 'location_type':[], 'latitude':[], 'longitude':[], 'hours_of_operation':[]}
        
    driver=webdriver.Chrome('C:\webdrivers\chromedriver.exe')
    driver.get('http://plexhiwire.com/')
    
    location_data_urls=[i.get_attribute('href') for i in driver.find_elements_by_xpath('//a[@class="location-btn"]')]
    
    for url in location_data_urls:
        driver.get(url)
        location_data=[i.text for i in driver.find_elements_by_xpath('//div[@class="col-lg-3 footer-menu"]')]    
        for i in location_data:
            
            data['locator_domain'].append('http://plexhiwire.com/')
            data['location_name'].append(url.split('/')[-1])
            data['street_address'].append(i.split('\n')[1])
            data['city'].append(i.split('\n')[2].split(',')[0])
            data['state'].append(i.split('\n')[2].split(',')[1].split()[0])
            data['zip'].append(i.split('\n')[2].split(',')[1].split()[1])
            data['country_code'].append('US')
            data['store_number'].append('<MISSING>')
            data['phone'].append(i.split('\n')[3])
            data['location_type'].append('<INACCESSIBLE>')
            data['longitude'].append('<MISSING>')
            data['latitude'].append('<MISSING>')
            data['hours_of_operation'].append('<MISSING>')
            
    driver.close()
    return data


def scrape():
    data = fetch_data()
    write_output(data)
scrape()