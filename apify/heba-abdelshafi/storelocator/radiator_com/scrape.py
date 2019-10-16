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

    driver.get('https://www.radiator.com/Locations')
    location_data=[i.text for i in driver.find_elements_by_xpath('//div[@class="locationLinkContainer"]')]
    
    for i in location_data:
        data['locator_domain'].append('https://www.radiator.com/')
        data['location_name'].append(i.split('|')[0])
        data['phone'].append(i.split('|')[-1])
        #data['zip'].append(i.split('|')[1].split(',')[-1].split()[-1])
        #data['street_address'].append(i.split('|')[1].split(',')[:-1])
        #data['country_code'].append('US')
        data['store_number'].append('<MISSING>')
        data['location_type'].append('<MISSING>')
        data['hours_of_operation'].append('<MISSING>')
        
           
    urls=[i.get_attribute('href') for i in driver.find_elements_by_xpath('//div[@class="locationLinkContainer"]/a')]
    for url in urls:
        driver.get(url)
        data['latitude'].append(driver.find_element_by_xpath('//input[@class="address-latitude"]').get_attribute('value'))
        data['longitude'].append(driver.find_element_by_xpath('//input[@class="address-longitude"]').get_attribute('value'))
        data['state'].append(driver.find_element_by_xpath('//span[@class="address-state"]').text)
        data['city'].append(driver.find_element_by_xpath('//span[@class="address-city"]').text)
        data['street_address'].append(driver.find_element_by_xpath('//span[@class="address-address"]').text)
        data['zip'].append(driver.find_element_by_xpath('//span[@class="address-zip"]').text)
        
    us_status=['alabama', 'alaska', 'arizona', 'arkansas', 'armed forces america', 'armed forces europe', 'armed forces pacific', 'california', 'colorado', 'connecticut', 'delaware', 'district of columbia', 'florida', 'georgia', 'hawaii', 'idaho', 'illinois', 'indiana', 'iowa', 'kansas', 'kentucky', 'louisiana', 'maine', 'maryland', 'massachusetts', 'michigan', 'minnesota', 'mississippi', 'missouri', 'montana', 'nebraska', 'nevada', 'new hampshire', 'new jersey', 'new mexico', 'new york', 'north carolina', 'north dakota', 'ohio', 'oklahoma', 'oregon', 'pennsylvania', 'rhode island', 'south carolina', 'south dakota', 'tennessee', 'texas', 'utah', 'vermont', 'virginia', 'washington', 'west virginia', 'wisconsin', 'wyoming']
    can_status=['province', 'alberta', 'british columbia', 'manitoba', 'new brunswick', 'newfoundland and labrador', 'northwest territories', 'nova scotia', 'nunavut', 'ontario', 'prince edward island', 'quebec', 'saskatchewan', 'yukon']
    
    for ind,i in enumerate(data['state']):
        i=i.lower()
        if i in can_status:
            data['country_code'].append('CAN')
        elif i in us_status:
            data['country_code'].append('US')
        else:
            data['country_code'].append('US')
            
   
    driver.close()
    return data


def scrape():
    data = fetch_data()
    write_output(data)
scrape()