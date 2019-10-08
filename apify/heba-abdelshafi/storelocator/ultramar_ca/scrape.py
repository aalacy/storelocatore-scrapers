from selenium import webdriver
from time import sleep
import pandas as pd


from selenium.webdriver.chrome.options import Options
options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
#driver=webdriver.Chrome('C:\chromedriver.exe', options=options)
driver = webdriver.Chrome("chromedriver", options=options)


def write_output(data):
    df=pd.DataFrame(data)
    df.to_csv('data.csv', index=False, encoding='utf-8-sig')


def fetch_data():
    data={'locator_domain':[],'location_name':[],'street_address':[],'city':[], 'state':[], 'zip':[], 'country_code':[], 'store_number':[],'phone':[], 'location_type':[], 'latitude':[], 'longitude':[], 'hours_of_operation':[]}
    
    country=['canada','US']
    for co in country:
        driver.get('https://www.ultramar.ca/en-on/find-services-stations/?locator_q={}'.format(co))
        
        while True:
            try:
                driver.find_element_by_xpath('//a[@class="localization__load-more-link btn button__main--blue js-load-more-trigger"]').click()
            except:
                break
        
        location_data=[i.text for i in driver.find_elements_by_xpath('//li[@class="localization__right-col-item"]')]
        location_data_urls=[i.get_attribute('href') for i in driver.find_elements_by_xpath('//h2[@class="localization__right-col-item-second-section-title heading__title--result"]/a')]
        
        for i in location_data_urls:
            data['locator_domain'].append('https://www.ultramar.ca')
            driver.get(i)
            location_data=driver.find_element_by_xpath('//div[@class="station__coordinates"]').text.split('\n')
            data['location_name'].append(driver.find_element_by_xpath('//h1[@class="station__title"]').text)
            data['street_address'].append(location_data[1])
            data['city'].append(location_data[2].split(',')[0])
            data['state'].append(location_data[2].split(',')[1].split()[0])
            data['zip'].append(location_data[2].split(',')[1].split()[1])
            data['phone'].append(location_data[3])
            try:
                data['hours_of_operation'].append(driver.find_element_by_xpath('////div[@class="station__hours"]').text)
            except:
                data['hours_of_operation'].append(driver.find_element_by_xpath('//div[@class="station__icon-text"]').text)
            data['location_type'].append(driver.find_element_by_xpath('//div[@class="text-center"]/a').text.split(' ',2)[-1])
            data['country_code'].append('{}'.format(co))
            data['store_number'].append('<MISSING>')
            data['longitude'].append(driver.find_element_by_xpath('//div[@class="language_selector"]/a').get_attribute('href').split('=')[-1])
            data['latitude'].append(driver.find_element_by_xpath('//div[@class="language_selector"]/a').get_attribute('href').split('=')[1].split('&')[0])
     


    driver.close()
    return data


def scrape():
    data = fetch_data()
    write_output(data)
scrape()
