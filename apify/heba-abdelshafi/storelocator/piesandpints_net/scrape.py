from selenium import webdriver
import pandas as pd
from time import sleep
import re


from selenium.webdriver.chrome.options import Options
options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument("user-agent= 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'")
#driver=webdriver.Chrome('C:\chromedriver.exe')#, options=options)
driver = webdriver.Chrome("chromedriver", options=options)

def parse_geo(url):
    lon = re.findall(r'\,(--?[\d\.]*)', url)[0]
    lat = re.findall(r'\@(-?[\d\.]*)', url)[0]
    return lat, lon

def write_output(data):
    df=pd.DataFrame(data)
    df.to_csv('data.csv', index=False,encoding='utf-8')

def fetch_data():
    data={'locator_domain':[],'location_name':[],'street_address':[],'city':[], 'state':[], 'zip':[], 'country_code':[], 'store_number':[],'phone':[], 'location_type':[], 'latitude':[], 'longitude':[], 'hours_of_operation':[],'page_url':[]}
    driver.get('https://piesandpints.net/store-locations/')

    locations_urls=[i.get_attribute('href') for i in driver.find_elements_by_xpath("//ul[@class='social-location']//a[contains(@href,'beermenus')]")]

    for url in locations_urls:
        driver.get(url)
        data['locator_domain'].append('https://piesandpints.net')
        data['page_url'].append(url)
        data['location_name'].append(driver.find_element_by_xpath('//h1[@class="mb-0 text-biggest"]').text)
        loc_data=driver.find_element_by_xpath('//li[@class="pure-list-item lead-by-icon"][1]').text
        geo_data=driver.find_element_by_xpath('//li[@class="pure-list-item lead-by-icon"][1]/a').get_attribute('href')
        data['location_type'].append(loc_data.split('·')[0])
        data['street_address'].append(loc_data.split('·')[1].split(',')[0])
        data['city'].append(loc_data.split('·')[1].split(',')[1])
        data['state'].append(loc_data.split('·')[1].split(',')[2].split()[0])
        data['zip'].append(loc_data.split('·')[1].split(',')[2].split()[1])
        try:
            data['phone'].append(driver.find_element_by_xpath('//li[@class="pure-list-item lead-by-icon"][3]').text)
        except:
            data['phone'].append('<MISSING>')
        try:
            data['hours_of_operation'].append(driver.find_element_by_xpath('//li[@class="pure-list-item lead-by-icon"][4]').text)
        except:
            data['hours_of_operation'].append('<MISSING>')
        data['country_code'].append('US')
        data['store_number'].append('<MISSING>')
        driver.get(geo_data)
        sleep(5)
        lat, lon = parse_geo(driver.current_url)
        data['latitude'].append(lat)
        data['longitude'].append(lon)

    driver.close()
    return data


def scrape():
    data = fetch_data()
    write_output(data)
scrape()
