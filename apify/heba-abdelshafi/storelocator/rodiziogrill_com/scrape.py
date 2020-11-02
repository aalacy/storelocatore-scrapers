from selenium import webdriver
import pandas as pd
import re
from time import sleep


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

def replace(string, substitutions):
    substrings = sorted(substitutions, key=len, reverse=True)
    regex = re.compile('|'.join(map(re.escape, substrings)))
    return regex.sub(lambda match: substitutions[match.group(0)], string)

def fetch_data():
    data={'locator_domain':[],'location_name':[],'street_address':[],'city':[], 'state':[], 'zip':[], 'country_code':[], 'store_number':[],'phone':[], 'location_type':[], 'latitude':[], 'longitude':[], 'hours_of_operation':[],'page_url':[]}
    driver.get('https://www.rodiziogrill.com/locations.aspx')
    location_data_urls=[]
    location_cities=[]
    for i in driver.find_elements_by_xpath('//div[@class="row"]//ul/li'):
        location_name=i.text
        if ('COMING SOON' not in location_name):
            location_cities.append(location_name)
            location_data_urls.append(i.find_element_by_css_selector('a').get_attribute('href'))

    for ind,i in enumerate(location_data_urls):
        driver.get(i)
        data['location_name'].append('Rodizio Grill'+' - '+location_cities[ind])
        addre=driver.find_element_by_xpath("//div[contains(@class, 'col-md-3 col-md-offset-0 Column4')]/div[2]").text.split('\n')
        data['street_address'].append(addre[0])
        data['city'].append(addre[-1].split(',')[0])
        data['state'].append(addre[-1].split(',')[1].split()[0])
        data['zip'].append(addre[-1].split(',')[1].split()[1])
        try:
            data['phone'].append(driver.find_element_by_xpath('//div[@class="locationPhone"]/a').text)
        except:
            data['phone'].append(driver.find_element_by_xpath('//div[@class="locationPhone"]').text.split('.')[-1])
        data['locator_domain'].append('https://www.rodiziogrill.com')
        data['page_url'].append(i)
        data['country_code'].append('US')
        stri=driver.find_element_by_xpath("//div[contains(@class, 'col-md-3 col-md-offset-0 Column2')]").text
        rep={'HOURS':'','BREAKFAST HOURS':'','*Dinner Pricing All Day on Easter, Mother\'s Day and Father\'s Day.\nReservations Recommended':'','**Holiday hours may vary':'','Private Group Events of 40 or more may be booked during lunch hours Monday through Wednesday in advance. Please call for details.':'','*Join us Saturday & Sunday for our special extended brunch menu!':'','CLOSED SUNDAY':''}
        data['hours_of_operation'].append(replace(stri,rep))
        data['location_type'].append(driver.find_element_by_xpath('//a[@class="logo"]/img').get_attribute('alt'))
        data['store_number'].append('<MISSING>')
        source = str(driver.page_source.encode("utf-8"))
        geo=re.sub('[A-Za-z)(]','',re.findall(r"LatLng\(-?[\d\.]+,\s-?[\d\.]+\)", source)[0])
        data['longitude'].append(geo.split(',')[1])
        data['latitude'].append(geo.split(',')[0])

    driver.close()
    return data

def scrape():
    data = fetch_data()
    write_output(data)
scrape()
