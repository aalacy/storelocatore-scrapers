from selenium import webdriver
from time import sleep
import pandas as pd


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
    
    driver.get('https://swiha.edu/contact/')
    location_data=[i.text for i in driver.find_elements_by_xpath('//div[@class="large-4 small-4 columns"]/div[@class="blue panel radius"]/p')]

    for i in location_data:
        data['locator_domain'].append('https://swiha.edu')
        data['location_name'].append(i.split('\n')[0])
        data['street_address'].append(i.split('\n')[1])
        data['city'].append(i.split('\n')[2].split(',')[0])
        data['state'].append(i.split('\n')[2].split(',')[1].split()[0])
        data['zip'].append(i.split('\n')[2].split(',')[1].split()[1])
        data['country_code'].append('US')
        data['store_number'].append('<MISSING>')
        data['phone'].append(i.split('\n')[4])
        data['location_type'].append(i.split('\n')[5].split('.')[0])
        data['longitude'].append('<MISSING>')
        data['latitude'].append('<MISSING>')
        data['hours_of_operation'].append('<MISSING>')   
    
    driver.close()
    return data


def scrape():
    data = fetch_data()
    write_output(data)
scrape()