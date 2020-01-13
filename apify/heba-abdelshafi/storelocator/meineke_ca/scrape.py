from selenium import webdriver
from time import sleep
import pandas as pd
import itertools


from selenium.webdriver.chrome.options import Options
options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument("user-agent= 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'")
driver = webdriver.Chrome("chromedriver", options=options)

#driver=webdriver.Chrome('C:\webdrivers\chromedriver.exe')#, options=options)


def write_output(data):
    df=pd.DataFrame(data).drop_duplicates()
    df.to_csv('data.csv', index=False)


def fetch_data():

    data={'locator_domain':[],'location_name':[],'street_address':[],'city':[], 'state':[], 'zip':[], 'country_code':[], 'store_number':[],'phone':[], 'location_type':[], 'latitude':[], 'longitude':[], 'hours_of_operation':[],'page_url':[]}
    driver.get('https://www.meineke.ca/locations/')
    status_url=[i.get_attribute('href') for i in driver.find_elements_by_xpath('//div[@class="col-md-4 col-sm-5 left-list "]//li/a')]

    city_urls=[]
    for city in status_url:
        driver.get(city)
        city_urls.append([i.get_attribute('href') for i in driver.find_elements_by_xpath('//div[@class="desktop-tablet"]//li/a[@class="city-link"]')])
    city_urls=list(itertools.chain.from_iterable(city_urls))

    locations=[]
    for loc in city_urls:
        driver.get(loc)
        sleep(3)
        locations.append([i.get_attribute('ng-click')[i.get_attribute('ng-click').find("(")+1:i.get_attribute('ng-click').find("rawSemCamPhone")].replace('\'','').split(',') for i in driver.find_elements_by_xpath("//div[contains(@ng-click, 'vm.reloadMap')]")])
        data['hours_of_operation'].append([i.text.replace('Store Hours\n','') for i in driver.find_elements_by_xpath('//div[@class="segment-store"]')])
        data['page_url'].append([i.get_attribute('href') for i in driver.find_elements_by_xpath('//div[@class="segment-store-info"]/a')])
    locations=list(itertools.chain.from_iterable(locations))
    data['hours_of_operation']=list(itertools.chain.from_iterable(data['hours_of_operation']))
    data['page_url']=list(itertools.chain.from_iterable(data['page_url']))

    for i in locations:
        data['locator_domain'].append('https://www.meineke.com')
        data['location_name'].append('Meineke')
        data['country_code'].append('CAN')
        data['location_type'].append('Car Care Center')
        data['latitude'].append(i[0].strip())
        data['longitude'].append(i[1].strip())
        data['store_number'].append(i[2].strip())
        data['city'].append(i[3].split(':')[-1])

        if len(i)==13:
            data['street_address'].append(i[4].split(':')[-1])
            data['state'].append(i[6].split(':')[-1])
            if i[7].split(':')[-1]=='':
                data['zip'].append('<MISSING>')
            else:
                data['zip'].append(i[7].split(':')[-1])
            data['phone'].append(i[9].split(':')[-1])
        elif len(i)==14:
            data['street_address'].append(i[4].split(':')[-1]+' '+i[5])
            data['state'].append(i[7].split(':')[-1])
            if i[7].split(':')[-1]=='':
                data['zip'].append('<MISSING>')
            else:
                data['zip'].append(i[8].split(':')[-1])
            data['phone'].append(i[10].split(':')[-1])


    driver.close()
    return data


def scrape():
    data = fetch_data()
    write_output(data)
scrape()
