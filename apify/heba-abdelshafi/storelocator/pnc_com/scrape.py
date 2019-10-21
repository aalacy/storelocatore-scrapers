from selenium import webdriver
from time import sleep
import pandas as pd

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from selenium.webdriver.chrome.options import Options
options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
#driver=webdriver.Chrome('C:\chromedriver.exe', options=options)
driver = webdriver.Chrome("chromedriver", options=options)


def fetch_data():
    data={'locator_domain':[],'location_name':[],'street_address':[],'city':[], 'state':[], 'zip':[], 'country_code':[], 'store_number':[],'phone':[], 'location_type':[], 'latitude':[], 'longitude':[], 'hours_of_operation':[]}
    url='https://apps.pnc.com/locator/#/browse'
    driver.get(url)   
    sleep(5)            
    states=[i.text for i in driver.find_elements_by_xpath('//div[@class="desktopView"]//a[@class="ng-binding"]')]
    
    for state in states:
        driver.get('https://apps.pnc.com/locator/#/browse/{}'.format(state))
        sleep(3)
        cities=[(' ').join(i.text.split()[:-1]) for i in driver.find_elements_by_xpath('//div[@class="desktopView"]//a[@class="ng-binding"]')]
        try:
            sleep(3)
            element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//div[@class="desktopView"]//a[@class="ng-binding"]')))
            no_of_branches=[int(i.text.split()[-1][1]) for i in driver.find_elements_by_xpath('//div[@class="desktopView"]//a[@class="ng-binding"]')]
        except:
            sleep(3)
            driver.refresh()
            element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//div[@class="desktopView"]//a[@class="ng-binding"]')))
            try:
                no_of_branches=[int(i.text.split()[-1][1]) for i in driver.find_elements_by_xpath('//div[@class="desktopView"]//a[@class="ng-binding"]')]
            except:
                sleep(3)
                no_of_branches=[int(i.text.split()[-1][1]) for i in driver.find_elements_by_xpath('//div[@class="desktopView"]//a[@class="ng-binding"]')]
    
        for index,city in enumerate(cities):
                url='https://apps.pnc.com/'   
                driver.get('https://apps.pnc.com/locator/#/browse/{}/{}'.format(state,city))
                sleep(5)
                if no_of_branches[index]>1:
                    for i in range (1,no_of_branches[index]+1): 
                        try:
                            element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//div[@class="desktopView"]//div[@class="card ng-scope"]')))
                        except:
                            driver.refresh()
                            try:
                                element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//div[@class="desktopView"]//div[@class="card ng-scope"]')))
                            except:
                                continue
                        location_data=driver.find_element_by_xpath('//div[@class="desktopView"]//div[@class="card ng-scope"][{}]'.format(i)).text.split('\n')
                        if len (location_data)==7:
                            data['locator_domain'].append(url)
                            data['state'].append(state)
                            data['city'].append(city)
                            data['location_name'].append(location_data[0])
                            data['location_type'].append(location_data[1].split()[-1])
                            data['street_address'].append(location_data[2])
                            data['zip'].append(location_data[3].split()[-1])
                            data['phone'].append(location_data[4])
                            try:
                                data['hours_of_operation'].append(location_data[5].replace('Lobby Open Today:',''))
                            except:
                                data['hours_of_operation'].append(location_data[5])
                            data['latitude'].append('<INACCESSIBLE>')
                            data['longitude'].append('<INACCESSIBLE>')
                            data['store_number'].append('<INACCESSIBLE>')
                            data['country_code'].append('US')
                       
                    
                else:
                    try:
                        element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//div[@class="desktopView"]//div[@class="card ng-scope"]')))
                    except:
                        driver.refresh()
                        try:
                            element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//div[@class="desktopView"]//div[@class="card ng-scope"]')))
                        except:
                            continue                        
                    location_data=driver.find_element_by_xpath('//div[@class="desktopView"]//div[@class="card ng-scope"]').text.split('\n')
                    if len (location_data)==7:
                        data['locator_domain'].append(url)
                        data['state'].append(state)
                        data['city'].append(city)
                        data['location_name'].append(location_data[0])
                        data['location_type'].append(location_data[1].split()[-1])
                        data['street_address'].append(location_data[2])
                        data['zip'].append(location_data[3].split()[-1])
                        data['phone'].append(location_data[4])
                        try:
                            data['hours_of_operation'].append(location_data[5].split(' ',3)[-1].replace('Lobby Open Today:',''))
                        except:
                            data['hours_of_operation'].append(location_data[5].split(' ',3)[-1])
                        data['latitude'].append('<INACCESSIBLE>')
                        data['longitude'].append('<INACCESSIBLE>')
                        data['store_number'].append('<INACCESSIBLE>')
                        data['country_code'].append('US')   
                
    driver.close()
    return data
    

def write_output(data):
    df=pd.DataFrame(data)
    df.to_csv('data.csv', index=False)
                
def scrape():
    data = fetch_data()
    write_output(data)
scrape()
