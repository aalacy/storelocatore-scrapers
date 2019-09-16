from selenium import webdriver
from time import sleep
import pandas as pd


def write_output(data):
    df=pd.DataFrame(data)
    df.to_csv('data.csv', index=False)
    
def fetch_data():
    data={'locator_domain':[],'location_name':[],'street_address':[],'city':[], 'state':[], 'zip':[], 'country_code':[], 'store_number':[],'phone':[], 'location_type':[], 'latitude':[], 'longitude':[], 'hours_of_operation':[]}

    driver=webdriver.Chrome('C:\webdrivers\chromedriver.exe')
    driver.get('https://www.radiator.com/Locations')
    location_data=[i.text for i in driver.find_elements_by_xpath('//div[@class="locationLinkContainer"]')]
    
    for i in location_data:
        data['locator_domain'].append('https://www.radiator.com/')
        data['location_name'].append(i.split('|')[0])
        data['phone'].append(i.split('|')[-1])
        #data['zip'].append(i.split('|')[1].split(',')[-1].split()[-1])
        #data['street_address'].append(i.split('|')[1].split(',')[:-1])
        data['country_code'].append('US')
        data['store_number'].append('<MISSING>')
        data['location_type'].append('<MISSING>')
        data['hours_of_operation'].append('<MISSING>')
        
           
    urls=[i.get_attribute('href') for i in driver.find_elements_by_xpath('//div[@class="locationLinkContainer"]/a')]
    for url in urls:
        driver.get(url)
        data['latitude'].append(driver.find_element_by_xpath('//input[@class="address-latitude"]').get_attribute('value'))
        data['longitude'].append(driver.find_element_by_xpath('//input[@class="address-longitude"]').get_attribute('value'))
        data['state'].append(driver.find_element_by_xpath('//span[@class="address-state"]').text)
        data['city'].append(driver.find_element_by_xpath('//span[@class="address-city"]').text)
        data['street_address'].append(driver.find_element_by_xpath('//span[@class="address-address"]').text)
        data['zip'].append(driver.find_element_by_xpath('//span[@class="address-zip"]').text)
        
        
    driver.close()
    return data


def scrape():
    data = fetch_data()
    write_output(data)
scrape()