from selenium import webdriver
from time import sleep
import pandas as pd
import itertools
import re


from selenium.webdriver.chrome.options import Options
options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument("user-agent= 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'")
driver = webdriver.Chrome("chromedriver", options=options)

#driver=webdriver.Chrome('C:\webdrivers\chromedriver.exe')#, options=options)


def write_output(data):
    df=pd.DataFrame(data)
    df.to_csv('data.csv', index=False)


def fetch_data():

    data={'locator_domain':[],'location_name':[],'street_address':[],'city':[], 'state':[], 'zip':[], 'country_code':[], 'store_number':[],'phone':[], 'location_type':[], 'latitude':[], 'longitude':[], 'hours_of_operation':[],'page_url':[]}
    
    driver.get('https://www.davita.com/tools/find-dialysis-center?')
    sleep(5)    
    driver.execute_script("arguments[0].click();",driver.find_element_by_xpath('//a[@class="ng-tns-c0-0"]'))    

    for state in driver.find_elements_by_xpath('//select[@name="state"]/option[@class="ng-tns-c0-0"]')[1:]:
        state.click()
        sleep(3)
        try:
            start=int(driver.find_element_by_xpath('//a[@class="div-pagination__item active-item"]').text)
            end=int(driver.find_element_by_xpath('//a[contains(@aria-label,"Last Page")]').text)
            
            for i in range(start,end+1): 
                    data['location_name'].append([i.text for i in driver.find_elements_by_xpath('//a[contains(@aria-label,"REQUEST TREATMENT DaVita")]')])
                    data['street_address'].append([i.text.split('\n')[0] for i in driver.find_elements_by_xpath('//div[@class="dv-results-card__info__col dv-results-card__info__body col-left"]/p[span[contains(text(),"")]]')])
                    data['city'].append([i.text.split('\n')[-1].split(',')[0] for i in driver.find_elements_by_xpath('//div[@class="dv-results-card__info__col dv-results-card__info__body col-left"]/p[span[contains(text(),"")]]')])
                    data['state'].append([i.text.split('\n')[-1].split(',')[-1].strip().split(' ')[0] for i in driver.find_elements_by_xpath('//div[@class="dv-results-card__info__col dv-results-card__info__body col-left"]/p[span[contains(text(),"")]]')])
                    data['zip'].append([i.text.split('\n')[-1].split(',')[-1].strip().split(' ')[-1] for i in driver.find_elements_by_xpath('//div[@class="dv-results-card__info__col dv-results-card__info__body col-left"]/p[span[contains(text(),"")]]')])        
                    data['store_number'].append([i.text for i in driver.find_elements_by_xpath('//strong[contains(text(),"Reference Number:")]/following-sibling::span')])
                    data['phone'].append([i.text for i in driver.find_elements_by_xpath('//strong[contains(text(),"Phone:")]/following-sibling::a')])
                    data['longitude'].append([re.findall(r'(-[\d\.]+|[\d\.]+)',i.get_attribute('data-analytics'))[-1] for i in driver.find_elements_by_xpath('//a[@class="dv-results-card__directions"]')])
                    data['latitude'].append([re.findall(r'(-[\d\.]+|[\d\.]+)',i.get_attribute('data-analytics'))[-2] for i in driver.find_elements_by_xpath('//a[@class="dv-results-card__directions"]')])
            
                    for i in range (len ([i.text for i in driver.find_elements_by_xpath('//a[contains(@aria-label,"REQUEST TREATMENT DaVita")]')])):
                        data['location_type'].append(driver.find_element_by_xpath('//h1[@class="dv-finder--search__title"]/span').text.split('\n')[-1])
                        data['locator_domain'].append('https://www.davita.com')
                        data['country_code'].append('US')
                        data['hours_of_operation'].append('missing')
                        data['page_url'].append(driver.current_url)    
                    driver.execute_script("arguments[0].click();",driver.find_element_by_xpath('//a[@class="btn btn--white"][contains(text(),"Next")]'))
        except:
            pass
        
    data['location_name']=list(itertools.chain.from_iterable(data['location_name']))
    data['street_address']=list(itertools.chain.from_iterable(data['street_address']))
    data['city']=list(itertools.chain.from_iterable(data['city']))
    data['state']=list(itertools.chain.from_iterable(data['state']))
    data['zip']=list(itertools.chain.from_iterable(data['zip']))
    data['store_number']=list(itertools.chain.from_iterable(data['store_number']))
    data['phone']=list(itertools.chain.from_iterable(data['phone']))
    data['longitude']=list(itertools.chain.from_iterable(data['longitude']))
    data['latitude']=list(itertools.chain.from_iterable(data['latitude']))
    


    driver.close()
    return data


def scrape():
    data = fetch_data()
    write_output(data)
scrape()
