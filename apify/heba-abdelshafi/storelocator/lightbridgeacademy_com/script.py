from selenium import webdriver
from time import sleep
import pandas as pd

def write_output(data):
    df=pd.DataFrame(data)
    df.to_csv('data.csv', index=False)
 
    
def fetch_data():
    data={'locator_domain':[],'location_name':[],'street_address':[],'city':[], 'state':[], 'zip':[], 'country_code':[], 'store_number':[],'phone':[], 'location_type':[], 'latitude':[], 'longitude':[], 'hours_of_operation':[]}
        
    driver=webdriver.Chrome('C:\webdrivers\chromedriver.exe')
    driver.get('http://lightbridgeacademy.com/center-locator/')
    def data_info():
        while True:
            location_data=[i.text for i in driver.find_elements_by_xpath('//div[@id="locator_3"]/div')]
            try:
                driver.find_element_by_xpath('//a[@class="more_centers btn"]').click()
            except:
                break
        yield location_data
    locations=list(data_info())[0]

    hrs=['<MISSING>' if i.text=='' else i.text for i in driver.find_elements_by_xpath('//div[@class="hours"]')]
    code = driver.execute_script("return initMap.toString()")
    markers = driver.execute_script('\n'.join(code.splitlines()[1:-1]) + '\n return markers;')
    
    for ind,i in enumerate(locations):
            loc=i.split('\n')
            data['locator_domain'].append('http://lightbridgeacademy.com')
            data['location_name'].append(loc[0])
            data['street_address'].append(loc[1])
            data['city'].append(loc[2].split(',')[0])
            data['state'].append(loc[2].split(',')[1].split()[0])
            data['zip'].append(loc[2].split(',')[1].split()[1])
            data['country_code'].append('US')
            data['store_number'].append('<MISSING>')
            data['phone'].append(loc[4].split(':')[-1])
            data['hours_of_operation'].append(hrs[ind])
            data['location_type'].append('Lightbridge Academy Center')
                        
    for i in data['location_name']:
        for j in markers:
            if j[0]==i:
                data['longitude'].append(j[1])
                data['latitude'].append(j[2])
               
                
    driver.close()
    return data
    

def scrape():
    data = fetch_data()
    write_output(data)
scrape()

 
        
