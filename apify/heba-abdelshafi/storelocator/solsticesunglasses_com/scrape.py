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

    driver.get('https://www.solsticesunglasses.com/store-finder')

    location_data=[i.text for i in driver.find_elements_by_xpath('//span[@class="entry__info"]')]

    for i in location_data:
        data['locator_domain'].append('https://www.solsticesunglasses.com')
        loc=i.split('\n')
        data['location_name'].append(loc[0])
        data['phone'].append(loc[1])
        data['street_address'].append(loc[2])
        data['city'].append(loc[3].split(',')[0])
        data['zip'].append(loc[3].split(',')[1])
        data['location_type'].append(driver.find_element_by_xpath('//li[@class="active"]').text.split()[0])
        data['state'].append('<MISSING>')
        data['country_code'].append('US')
        data['store_number'].append('<MISSING>')
        data['longitude'].append('<MISSING>')
        data['latitude'].append('<MISSING>')
        #data['hours_of_operation'].append('<INACCESSIBLE>')
    for i in driver.find_elements_by_xpath('//a[@onclick="return false"]'):
        i.click()
        sleep(3)
        data['hours_of_operation'].append((' '.join(driver.find_element_by_xpath('//div[@class="gm-style-iw-d"]').text.split('\n')[5:])))
 


    driver.close()
    return data


def scrape():
    data = fetch_data()
    write_output(data)
scrape()
