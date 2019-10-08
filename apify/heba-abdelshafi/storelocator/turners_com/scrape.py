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
    df.to_csv('data.csv', index=False,encoding='utf-8-sig')


def fetch_data():
    data={'locator_domain':[],'location_name':[],'street_address':[],'city':[], 'state':[], 'zip':[], 'country_code':[], 'store_number':[],'phone':[], 'location_type':[], 'latitude':[], 'longitude':[], 'hours_of_operation':[]}
    driver.get('https://www.turners.com/storelocator.cfm?locRad=100&locZip=&locSt=CA')

    location_data=[i.text for i in driver.find_elements_by_xpath('//div[@class="mapAddress"]')]

    location_data_urls=[i.get_attribute('href') for i in driver.find_elements_by_xpath('//a[text()="Get Directions"]')]

    for i in location_data:
        data['locator_domain'].append('https://www.turners.com')
        loc=i.split('\n')
        data['location_name'].append(loc[0])
        data['city'].append(loc[0].split(',')[0])
        data['street_address'].append(loc[2])
        data['state'].append('california')
        data['phone'].append(loc[3])
        data['country_code'].append('US')
        data['hours_of_operation'].append(loc[-3]+loc[-4]+loc[-5]+loc[-6])
        data['store_number'].append('<MISSING>')
        loc_type=driver.find_element_by_xpath('//div[@class="locatorForm"]/h1').text.split()
        data['location_type'].append(loc_type[4]+loc_type[5])


    for i in location_data_urls:
        #data['longitude'].append(re.split(r'\+*',i)[-1].split(',')[1].split('&')[0])
        #data['latitude'].append(re.split(r'\+*',i)[-1].split(',')[0].split('=')[-1])
        #data['zip'].append(re.split(r'\+*',i)[-1].split('&')[0])
        data['zip'].append(re.split(r'\++', i)[-1].split('&')[0])
        data['latitude'].append(re.split(r'\++', i)[-1].split(',')[0].split('=')[-1])
        data['longitude'].append(re.split(r'\++', i)[-1].split(',')[1].split('&')[0])


    driver.close()
    return data


def scrape():
    data = fetch_data()
    write_output(data)
scrape()
