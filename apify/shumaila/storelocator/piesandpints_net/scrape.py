from selenium import webdriver
import pandas as pd
from time import sleep
import re


from selenium.webdriver.chrome.options import Options
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('piesandpints_net')


options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument("user-agent= 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'")

#driver = webdriver.Chrome('c:\\Users\\Dell\\local\\chromedriver', options=options)
driver = webdriver.Chrome('chromedriver', options=options)



def write_output(data):
    df=pd.DataFrame(data)
    df.to_csv('data.csv', index=False,encoding='utf-8')

def fetch_data():
    
    p = 0
    data={'locator_domain':[],'location_name':[],'street_address':[],'city':[], 'state':[], 'zip':[], 'country_code':[], 'store_number':[],'phone':[], 'location_type':[], 'latitude':[], 'longitude':[], 'hours_of_operation':[],'page_url':[]}
    driver.get('https://piesandpints.net/store-locations/')


    locations_urls=[i.get_attribute('href') for i in driver.find_elements_by_xpath("//ul[@class='social-location']//a[contains(@href,'beermenus')]")]
    phone_urls = driver.find_elements_by_class_name('address-phone')
    phones = []
    for k in range(0,len(phone_urls)):
        phones.append(phone_urls[k].find_element_by_tag_name('a').get_attribute('href'))

    #for url in locations_urls:
    
    for k in range(0,len(locations_urls)):
        url = locations_urls[k]
        driver.get(url)
        #logger.info(url)
        sleep(1)
        data['locator_domain'].append('https://piesandpints.net')
        data['page_url'].append(url)
        try:
            span = driver.find_element_by_class_name('close')
            span.click()
        except:
            pass
        #oup = BeautifulSoup(driver.page_source,'html.parser')
        data['location_name'].append(driver.find_element_by_tag_name('h1').text)
        loc_data=driver.find_element_by_xpath('//li[@class="pure-list-item lead-by-icon"][1]').text
        geo_data=driver.find_element_by_xpath('//li[@class="pure-list-item lead-by-icon"][1]/a').get_attribute('href')
        storeid = driver.find_element_by_xpath('//li[@class="pure-list-item lead-by-icon"][1]/a').get_attribute('data-bar-id')
        #logger.info(storeid)
        data['store_number'].append(storeid)
        data['location_type'].append(loc_data.split('·')[0])
        data['street_address'].append(loc_data.split('·')[1].split(',')[0])
        data['city'].append(loc_data.split('·')[1].split(',')[1])
        data['state'].append(loc_data.split('·')[1].split(',')[2].split()[0])
        data['zip'].append(loc_data.split('·')[1].split(',')[2].split()[1])
        try:
            data['phone'].append(driver.find_element_by_xpath('//li[@class="pure-list-item lead-by-icon"][3]').text)
        except:
            data['phone'].append(phones[k].replace('tel:',''))
           # data['phone'].append('<MISSING>')

        #if data['phone'] == '<MISSING>':
            

        

        try:
            hours = driver.find_element_by_xpath('//li[@class="pure-list-item lead-by-icon"][4]').text
            hours = hours
            hours = hours.replace("\n"," ")
            #logger.info(hours)
            data['hours_of_operation'].append(hours)

        except:
            data['hours_of_operation'].append('<MISSING>')

        data['country_code'].append('US')

        
        data['latitude'].append('<MISSING>')
        data['longitude'].append('<MISSING>')
        

       

    driver.close()
    return data


def scrape():
    data = fetch_data()
    write_output(data)
scrape()
