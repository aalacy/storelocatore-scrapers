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

    driver.get('https://www.barresoul.com/contact')

    location_data=[i.text for i in driver.find_elements_by_xpath('//div[@class="col sqs-col-4 span-4"]/div[@class="sqs-block html-block sqs-block-html"]')]

    for i in location_data:
        data['locator_domain'].append('https://www.barresoul.com')
        if 'More info' in i:
            loc=i.split('\n')
            data['location_name'].append(loc[0])
            data['phone'].append(loc[2].split(':')[1])
            data['street_address'].append('<MISSING>')
            data['city'].append('<MISSING>')
            data['state'].append('<MISSING>')
            data['zip'].append('<MISSING>')
            data['country_code'].append('US')
            data['hours_of_operation'].append('<MISSING>')
            data['store_number'].append('<MISSING>')
            data['location_type'].append('<MISSING>')
            data['latitude'].append('<MISSING>')
            data['longitude'].append('<MISSING>')
        else:
            loc=i.split('\n')
            data['location_name'].append(loc[0])
            data['street_address'].append(loc[1])
            data['city'].append(loc[2].split(',')[0])
            data['state'].append(loc[2].split(',')[1].split()[0])
            data['zip'].append(loc[2].split(',')[1].split()[1])
            data['phone'].append(loc[3].split(':')[1])
            data['country_code'].append('US')
            data['hours_of_operation'].append('<MISSING>')
            data['store_number'].append('<MISSING>')
            data['location_type'].append('<MISSING>')
            data['latitude'].append('<MISSING>')
            data['longitude'].append('<MISSING>')


    driver.close()
    return data


def scrape():
    data = fetch_data()
    write_output(data)
scrape()
