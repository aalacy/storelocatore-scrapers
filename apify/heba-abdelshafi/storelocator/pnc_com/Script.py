from selenium import webdriver
from time import sleep
import pandas as pd

def fetch_data():
    data={'locator_domain':[],'location_name':[],'street_address':[],'city':[], 'state':[], 'zip':[], 'country_code':[], 'store_number':[],'phone':[], 'location_type':[], 'latitude':[], 'longitude':[], 'hours_of_operation':[]}

    driver=webdriver.Chrome('C:\webdrivers\chromedriver.exe')
    driver.get('https://apps.pnc.com/locator/#/browse')
    sleep(5)
               
    states=[i.text for i in driver.find_elements_by_xpath('//div[@class="desktopView"]//a[@class="ng-binding"]')]
    
    for state in states:
        driver.get('https://apps.pnc.com/locator/#/browse/{}'.format(state))
        sleep(3)
        cities=[(' ').join(i.text.split()[:-1]) for i in driver.find_elements_by_xpath('//div[@class="desktopView"]//a[@class="ng-binding"]')]
        no_of_branches=[int(i.text.split()[-1][1]) for i in driver.find_elements_by_xpath('//div[@class="desktopView"]//a[@class="ng-binding"]')]
        
        for index,city in enumerate(cities):
            url='https://apps.pnc.com/'   
            driver.get('https://apps.pnc.com/locator/#/browse/{}/{}'.format(state,city))
            sleep(5)
            if no_of_branches[index]>1:
                for i in range (1,no_of_branches[index]+1): 
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
                        data['hours_of_operation'].append(location_data[5])
                        data['latitude'].append('<MISSING>')
                        data['longitude'].append('<MISSING>')
                        data['store_number'].append('<MISSING>')
                        data['country_code'].append('US')
                    else:
                        pass
                    print(location_data)
                
            else:
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
                    data['hours_of_operation'].append(location_data[5].split(' ',3)[-1])
                    data['latitude'].append('<MISSING>')
                    data['longitude'].append('<MISSING>')
                    data['store_number'].append('<MISSING>')
                    data['country_code'].append('US')
                else:
                    pass
                print(location_data)
    driver.close()
    return data
    

def write_output(data):
    df=pd.DataFrame(data)
    df.to_csv('data.csv', index=False)
                
def scrape():
    data = fetch_data()
    write_output(data)
scrape()
