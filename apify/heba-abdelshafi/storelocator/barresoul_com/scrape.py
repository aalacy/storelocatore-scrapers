from selenium import webdriver
from time import sleep
import pandas as pd
import json


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
    data={'locator_domain':[],'location_name':[],'street_address':[],'city':[], 'state':[], 'zip':[], 'country_code':[], 'store_number':[],'phone':[], 'location_type':[], 'latitude':[], 'longitude':[], 'hours_of_operation':[],'page_url':[]}

    driver.get('https://www.barresoul.com')

    location_data_urls=[i.get_attribute('href') for i in driver.find_elements_by_xpath('//div[@id="headerNav"]//nav[@id="mainNavigation"]/div[@class="folder"][1]//div[@class="collection"]/a')]

    data={'locator_domain':[],'location_name':[],'street_address':[],'city':[], 'state':[], 'zip':[], 'country_code':[], 'store_number':[],'phone':[], 'location_type':[], 'latitude':[], 'longitude':[], 'hours_of_operation':[],'page_url':[]}
    loc=[]
    for i in location_data_urls:
        driver.get(i)
        #sleep(3)
        loc.append(driver.find_element_by_xpath('//div[@class="col sqs-col-6 span-6"]/div[contains(@class,"sqs-block")][@data-block-type="2"][contains(@id,"block")][2]').text.split('\n'))
        data['longitude'].append(json.loads(driver.find_element_by_xpath('//div[contains(@class,"sqs-block map-block sqs-block-map")]').get_attribute('data-block-json'))['location']['mapLat'])
        data['latitude'].append(json.loads(driver.find_element_by_xpath('//div[contains(@class,"sqs-block map-block sqs-block-map")]').get_attribute('data-block-json'))['location']['mapLng'])
        try:
            if "TWO LOCATIONS:" in driver.find_element_by_xpath('//div[@class="col sqs-col-6 span-6"]/div[contains(@class,"sqs-block")][@data-block-type="2"][contains(@id,"block")][2]').text:
                data['longitude'].append(json.loads(driver.find_element_by_xpath('//div[contains(@class,"sqs-block map-block sqs-block-map")]').get_attribute('data-block-json'))['location']['mapLat'])
                data['latitude'].append(json.loads(driver.find_element_by_xpath('//div[contains(@class,"sqs-block map-block sqs-block-map")]').get_attribute('data-block-json'))['location']['mapLng'])
        except:
            pass
    
    for ind,i in enumerate(loc):
        if len(i)==3:
            data['street_address'].append(i[0])
            data['city'].append(i[1].split(',')[0])
            data['state'].append(i[1].split(',')[1].split()[0])
            data['zip'].append(i[1].split(',')[1].split()[1])
            data['phone'].append(i[2].split('|')[0])

            data['locator_domain'].append('https://www.barresoul.com')
            data['country_code'].append('US')
            data['hours_of_operation'].append('<MISSING>')
            data['store_number'].append('<MISSING>')
            data['location_type'].append('<MISSING>')
            data['page_url'].append(location_data_urls[ind])
            data['location_name'].append(location_data_urls[ind].split('/')[-1])


        else:
            data['street_address'].append(i[1])
            data['city'].append(i[2].split(',')[0])
            data['state'].append(i[2].split(',')[1].split()[0])
            data['zip'].append(i[2].split(',')[1].split()[1])
            data['phone'].append(i[-1].split('|')[0])
            data['locator_domain'].append('https://www.barresoul.com')
            data['country_code'].append('US')
            data['hours_of_operation'].append('<MISSING>')
            data['store_number'].append('<MISSING>')
            data['location_type'].append('<MISSING>')
            data['page_url'].append(location_data_urls[ind])
            data['location_name'].append(location_data_urls[ind].split('/')[-1])


            data['street_address'].append(i[3])
            data['city'].append(i[4].split(',')[0])
            data['state'].append(i[4].split(',')[1].split()[0])
            data['zip'].append(i[4].split(',')[1].split()[1])
            data['phone'].append(i[-1].split('|')[0])
            data['locator_domain'].append('https://www.barresoul.com')
            data['country_code'].append('US')
            data['hours_of_operation'].append('<MISSING>')
            data['store_number'].append('<MISSING>')
            data['location_type'].append('<MISSING>')
            data['page_url'].append(location_data_urls[ind])
            data['location_name'].append(location_data_urls[ind].split('/')[-1])



    driver.close()
    return data


def scrape():
    data = fetch_data()
    write_output(data)
scrape()
