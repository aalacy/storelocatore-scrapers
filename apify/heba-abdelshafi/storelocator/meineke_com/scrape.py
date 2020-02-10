from selenium import webdriver
from time import sleep
import pandas as pd
import re


from selenium.webdriver.chrome.options import Options
options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
driver = webdriver.Chrome("chromedriver", options=options)

#driver=webdriver.Chrome('C:\webdrivers\chromedriver.exe')#, options=options)


def write_output(data):
    df=pd.DataFrame(data).drop_duplicates()
    df.to_csv('data.csv', index=False)


def fetch_data():

    data={'locator_domain':[],'location_name':[],'street_address':[],'city':[], 'state':[], 'zip':[], 'country_code':[], 'store_number':[],'phone':[], 'location_type':[], 'latitude':[], 'longitude':[], 'hours_of_operation':[],'page_url':[]}
    driver.get('https://www.meineke.com/locations/')
    status_url=[i.get_attribute('href') for i in driver.find_elements_by_xpath('//div[@class="col-md-4 col-sm-5 left-list "]//li/a')]

    city_urls=[]
    for city in status_url:
        driver.get(city)
        city_urls.extend([i.get_attribute('href') for i in driver.find_elements_by_xpath('//li/a[@class="city-link"]')])

    locations=[]
    for loc in city_urls:
        driver.get(loc)
        sleep(3)
        locations.extend([i.get_attribute('data-ng-click')[i.get_attribute('data-ng-click').find("(")+1:i.get_attribute('data-ng-click').find("rawSemCamPhone")].replace('\'','').split(',') for i in driver.find_elements_by_xpath("//div[contains(@data-ng-click, 'vm.reloadMap')]")])
        data['hours_of_operation'].extend([i.text.replace('Store Hours\n','') for i in driver.find_elements_by_xpath('//div[@class="segment-store"]')])
        data['page_url'].extend([i.get_attribute('href') for i in driver.find_elements_by_xpath('//div[@class="segment-store-info"]/a')]) 
        
    
    
    sub_loc=[]    
    for i in locations:
        data['locator_domain'].append('https://www.meineke.com')
        data['location_name'].append('Meineke')
        data['country_code'].append('US')
        data['location_type'].append('Car Care Center')
        data['latitude'].append(i[0])
        data['longitude'].append(i[1])
        data['store_number'].append(i[2])
        sub_loc.append(' '.join(i[3:]))
        
            
    for i in sub_loc:
        i=i.replace('&#39;','')
        data['city'].append(re.findall('locationCity: [\w\s.]+ ',i)[0].split(':')[-1])
        data['street_address'].append(re.findall('streetAddress1: [#.\w\s\d-]+ ',i)[0].split(':')[-1])
        data['state'].append(re.findall('locationState: [\w\s]+ ',i)[0].split(':')[-1])
        try:
            data['zip'].append(re.findall('locationPostalCode: [-\w\s]+ ',i)[0].split(':')[-1])
        except:
            data['zip'].append('<MISSING>')
        data['phone'].append(re.findall('rawPhone: \d+ ',i)[0].split(':')[-1])

    
#    
#    for i in locations:
#        data['locator_domain'].append('https://www.meineke.com')
#        data['location_name'].append('Meineke')
#        data['location_type'].append('Car Care Center')
#        data['country_code'].append('US')
#        
#        data['latitude'].append(i[0].strip())
#        data['longitude'].append(i[1].strip())
#        data['store_number'].append(i[2].strip())
#        data['city'].append(i[3].split(':')[-1])
#
#        if len(i)==14:
#            data['street_address'].append(i[5].split(':')[-1])
#            data['state'].append(i[7].split(':')[-1])
#            data['zip'].append(i[8].split(':')[-1])
#            data['phone'].append(i[9].split(':')[-1])
#
#        elif len(i)==15:
#            data['street_address'].append(i[5].split(':')[-1]+' '+i[6]+' '+i[7].split(':')[-1])
#            data['state'].append(i[8].split(':')[-1])
#            data['zip'].append(i[9].split(':')[-1])
#            data['phone'].append(i[10].split(':')[-1])
#        else:
#            data['street_address'].append(i[5].split(':')[-1]+' '+i[6]+' '+i[7])
#            data['state'].append(i[9].split(':')[-1])
#            data['zip'].append(i[10].split(':')[-1])
#            data['phone'].append(i[11].split(':')[-1])
                           
            
    driver.close()
    return data


def scrape():
    data = fetch_data()
    write_output(data)
scrape()
