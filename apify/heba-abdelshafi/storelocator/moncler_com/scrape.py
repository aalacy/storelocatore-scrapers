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

    driver.get('https://www.moncler.com/us/storeslocator/')
    globalvar = driver.execute_script("return SLData;")
    json_data=globalvar['stores']

    stores_data=[]
    for i in json_data:
        if i['countryCode']=='USA' or i['countryCode']=='CAN':
            stores_data.append(i)
            data['locator_domain'].append('https://www.moncler.com')
            data['location_name'].append(i['name'])
            data['street_address'].append(i['address'])
            data['city'].append(i['cityLangName'])
            if len(i['zip'])==4:
                data['zip'].append('0'+i['zip'])
            else:
                if r'&#39;' in i['zip']:
                    data['zip'].append(i['zip'].replace(r'&#39;',''))
                else:
                    data['zip'].append(i['zip'])

            data['country_code'].append(i['countryCode'])
            if len(i['phone'])>17:
                data['phone'].append(i['phone'].split('Ext')[0])
            else:
                data['phone'].append(i['phone'])
            data['hours_of_operation'].append(i['openingTimes'][0]['formatted'])
            data['state'].append('<MISSING>')
            data['store_number'].append(i['storeId'])
            data['location_type'].append(i['slug']['type'])
            data['longitude'].append(i['latLong']['lng'])
            data['latitude'].append(i['latLong']['lat'])

    driver.close()
    return data


def scrape():
    data = fetch_data()
    write_output(data)
scrape()
