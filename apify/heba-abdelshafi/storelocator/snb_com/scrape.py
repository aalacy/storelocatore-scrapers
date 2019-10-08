from selenium import webdriver
import pandas as pd
import re


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
    dfs=pd.read_html('https://snb.com/locations?range=20')[1]
    
    for i in range(len(dfs)):
        data['locator_domain'].append('https://snb.com')
        data['location_name'].append(dfs.Address[i].split('  ')[0])
        data['street_address'].append(dfs.Address[i].split('  ')[1].split(',')[0])
        data['city'].append((' ').join(dfs.Address[i].split('  ')[1].split(',')[1].split()[:-2]))
        data['state'].append('<MISSING>')
        data['zip'].append(dfs.Address[i].split('  ')[1].split(',')[1].split()[-2])
        data['country_code'].append('US')
        try:
            data['phone'].append((' ').join(re.findall(r'[0-9]+',dfs.Contact[i])))
            data['hours_of_operation'].append(dfs.Hours[i])
        except:
            data['phone'].append('<MISSING>')
            data['hours_of_operation'].append('<MISSING>')
        data['location_type'].append(dfs.Services[i])
        data['page_url'].append('https://snb.com/locations?range=20')
    
       
    driver=webdriver.Chrome('C:\chromedriver.exe')
    driver.get('https://snb.com/locations?range=20')
    globalvar = driver.execute_script("return locations;")
    
    for i in globalvar:
        data['latitude'].append(i['latitude'])
        data['longitude'].append(i['longitude'])
        data['store_number'].append(i['id'])
    
    
    driver.close()
    return data


def scrape():
    data = fetch_data()
    write_output(data)
scrape()
