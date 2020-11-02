from selenium import webdriver
from bs4 import BeautifulSoup
import json
import pandas as pd


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
    url = 'https://www.nbins.com/wp-admin/admin-ajax.php?lang=en&action=store_search&lat=43.65323&lng=-79.38318&max_results=500&search_radius=1000'
    driver.get(url)

    soup = BeautifulSoup(driver.page_source)
    locations_data= json.loads(soup.find("body").text)
    for i in locations_data:
        data['street_address'].append(i['address'])
        data['city'].append(i['city'])
        data['store_number'].append(i['id'])
        data['latitude'].append(i['lat'])
        data['longitude'].append(i['lng'])
        if i['phone']=='':
            data['phone'].append('<MISSING>')
        else:
            data['phone'].append(i['phone'])
        data['location_name'].append(i['store'])
        data['zip'].append(i['zip'])
        data['locator_domain'].append('https://www.nbins.com')
        data['page_url'].append(url)
        data['state'].append('<MISSING>')
        data['country_code'].append('CAN')
        data['location_type'].append('<MISSING>')
        data['hours_of_operation'].append('<MISSING>')



    driver.close()
    return data


def scrape():
    data = fetch_data()
    write_output(data)
scrape()
