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

    driver.get('https://www.sears.com/stores.html')
    driver.find_element_by_xpath('//span[@class="storeLocator"]/a').click()
    sleep(3)
    states=[i for i in driver.find_elements_by_xpath('//a[@itemprop="url"]')]
    for i in range (1,len(states)):
        states[i].click()
        location_data=[]
        for location in driver.find_elements_by_xpath('//li[@itemtype="http://schema.org/Store"]'):
            location_data.append(location.text.split('\n'))
        for i in location_data:
            data['locator_domain'].append('https://www.sears.com')
            data['location_name'].append(i[0].split(',')[0])
            #data['state_code'].append(i[0].split(',')[1])
            data['location_type'].append(i[1])
            data['street_address'].append(i[3])
            data['city'].append(i[4].split(',')[0])
            data['state'].append(i[4].split(',')[1].split()[0])
            data['zip'].append(i[4].split(',')[1].split()[1])
            try:
                data['phone'].append(i[5])
            except:
                data['phone'].append('<MISSING>')
            data['latitude'].append('<MISSING>')
            data['longitude'].append('<MISSING>')
            data['store_number'].append('<MISSING>')
            data['country_code'].append('US')
            data['hours_of_operation'].append('<INACCESSIBLE>')

        driver.execute_script("window.history.go(-1)")
        sleep(3)
        states=[i for i in driver.find_elements_by_xpath('//a[@itemprop="url"]')]
    driver.close()
    return data
        
            
def scrape():
    data = fetch_data()
    write_output(data)
scrape()