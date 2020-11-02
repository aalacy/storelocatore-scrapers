from selenium import webdriver
from time import sleep
import pandas as pd
import re

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

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
    driver.get('https://locations.rentacenter.com/')

    states_urls=[i.get_attribute('href') for i in driver.find_elements_by_xpath('//li[@class="list-group-item"]/a')]

    for state in states_urls:
        driver.get(state)
        sleep(5)
        try:
            location_data_urls=[]
            for i in range(2,100):
                driver.find_element_by_xpath('//li/a[@class="left"][text()={}]'.format(i)).click()
                for j in driver.find_elements_by_xpath('//div[@class="street"]/a'):
                    location_data_urls.append(j.get_attribute('href'))
        except:
            pass

        for url in location_data_urls:
            driver.get(url)
            sleep(3)
            element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//div[@class="list-data"]')))
            location_data=driver.find_element_by_xpath('//div[@class="list-data"]').text.split('\n')
            data['street_address'].append(location_data[0])
            data['location_name'].append(location_data[0])
            data['locator_domain'].append('https://www.rentacenter.com/')
            data['country_code'].append('US')
            data['city'].append(location_data[1].split(',')[0])
            data['state'].append(location_data[1].split(',')[1].split()[0])
            data['zip'].append(location_data[1].split(',')[1].split()[1])
            data['phone'].append(location_data[2])
            data['hours_of_operation'].append(location_data[5])
            data['store_number'].append('<MISSING>')
            data['location_type'].append('Rent-A-Center')
            data['longitude'].append('<INACCESSIBLE>')
            data['latitude'].append('<INACCESSIBLE>')


    driver.close()
    return data


def scrape():
    data = fetch_data()
    write_output(data)
scrape()
