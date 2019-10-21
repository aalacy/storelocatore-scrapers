from selenium import webdriver
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
options.add_argument("user-agent= 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'")
#driver=webdriver.Chrome('C:\chromedriver.exe', options=options)
driver = webdriver.Chrome("chromedriver", options=options)


def write_output(data):
    df=pd.DataFrame(data)
    df.to_csv('data.csv', index=False)


def fetch_data():
    data={'locator_domain':[],'location_name':[],'street_address':[],'city':[], 'state':[], 'zip':[], 'country_code':[], 'store_number':[],'phone':[], 'location_type':[], 'latitude':[], 'longitude':[], 'hours_of_operation':[],'page_url':[]}
    driver.get('https://richlandbank.com/locations/?view=all')

    location_data=[i.text.split('\n') for i in driver.find_elements_by_xpath('//div[@class="branch-info-container"]')]
    data['page_url']=[i.get_attribute('href') for i in driver.find_elements_by_xpath('//span[@class="sub-head fw-light"]/a')]

    for i in location_data:
        data['locator_domain'].append('https://richlandbank.com')
        data['country_code'].append('US')
        data['store_number'].append('<MISSING>')
        data['latitude'].append('<MISSING>')
        data['longitude'].append('<MISSING>')
        if 'ank' in i[1]:
            data['location_name'].append(i[0]+' '+i[1])
            data['street_address'].append(i[2])
            data['city'].append(i[3].split(',')[0])
            data['state'].append(i[3].split(',')[1].split()[0])
            data['zip'].append(i[3].split(',')[1].split()[1])
            if bool(re.search(r'[0-9]+', i[4]))==True:
                data['phone'].append((' ').join(re.findall(r'[0-9]+',i[4])))
                try:
                    data['location_type'].append(i[5])
                except:
                    data['location_type'].append('<MISSING>')
            else:
                data['phone'].append('<MISSING>')
                data['location_type'].append(i[-1])
        else:
            data['location_name'].append(i[0])
            data['street_address'].append(i[1])
            data['city'].append(i[2].split(',')[0])
            data['state'].append(i[2].split(',')[1].split()[0])
            data['zip'].append(i[2].split(',')[1].split()[1])
            data['phone'].append((' ').join(re.findall(r'[0-9]+',i[3])))
            data['location_type'].append(i[-1])


    for url in data['page_url']:
        driver.get(url)
        sleep(3)
        element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//div[contains(@class,"small-6 columns ")]/p[@class="fw-light"]')))
        try:
            data['hours_of_operation'].append(driver.find_element_by_xpath('//div[contains(@class,"small-6 columns ")]/p[@class="fw-light"]').text)
        except:
            data['hours_of_operation'].append('<MISSING>')


    driver.close()
    return data


def scrape():
    data = fetch_data()
    write_output(data)
scrape()
