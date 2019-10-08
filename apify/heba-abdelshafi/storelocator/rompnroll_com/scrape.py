from selenium import webdriver
import pandas as pd
import re
from bs4 import BeautifulSoup


from selenium.webdriver.chrome.options import Options
options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument("user-agent= 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'")
#driver=webdriver.Chrome('C:\chromedriver.exe', options=options)
driver = webdriver.Chrome("chromedriver", options=options)


def write_output(data):
    df=pd.DataFrame(data)
    df.to_csv('data.csv', index=False)


def fetch_data():
    data={'locator_domain':[],'location_name':[],'street_address':[],'city':[], 'state':[], 'zip':[], 'country_code':[], 'store_number':[],'phone':[], 'location_type':[], 'latitude':[], 'longitude':[], 'hours_of_operation':[],'page_url':[]}
    driver.get('https://rompnroll.com/locations')
    
    globalvar = driver.execute_script("return locations;")
    for i in globalvar:
         if i['coming_soon_display'] !='':
             data['location_name'].append(i['fran_location_name'])
             data['street_address'].append(i['fran_address'])
             data['city'].append(i['fran_city'])
             data['state'].append(i['fran_state'])
             data['country_code'].append(i['fran_country'])
             data['latitude'].append(i['fran_latitude'])
             data['longitude'].append(i['fran_longitude'])
             data['store_number'].append(i['fran_location_id'])
             data['phone'].append(i['fran_phone'])
             data['zip'].append(i['fran_zip'])
             soup = BeautifulSoup(globalvar[1]['fran_hours'], 'html.parser')       
             data['hours_of_operation'].append(re.sub('We are open','',soup.find('li').text))
             data['locator_domain'].append('https://rompnroll.com')
             data['page_url'].append('https://rompnroll.com/locations')
             data['location_type'].append('<MISSING>')
    
    driver.close()
    return data


def scrape():
    data = fetch_data()
    write_output(data)
scrape()
