import csv
import os
from bs4 import BeautifulSoup
import re, time
import datetime

from random import randint

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


def get_driver():
    options = Options() 
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=1920,1080')
    return webdriver.Chrome('chromedriver', chrome_options=options)


def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

driver = get_driver()
time.sleep(2)

def fetch_data():
    data = []
    store_links =[]
    clear_links =[]
    #CA stores
    url = 'https://www.petsmart.com/stores/us/'
    u='https://www.petsmart.com/'

    driver.get(url)
    time.sleep(randint(2,4))

    element = WebDriverWait(driver, 20).until(EC.presence_of_element_located(
        (By.CSS_SELECTOR, ".all-states-list.container")))
    time.sleep(randint(3,5))

    soup = BeautifulSoup(driver.page_source, "html.parser")
    store = soup.find('div',class_='all-states-list container')
    stores = store.find_all("a")
    for i in stores:
        newurl=i['href']
        print(newurl)

        driver.get(newurl)
        time.sleep(randint(2,4))

        element = WebDriverWait(driver, 20).until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, ".store-details-link")))
        time.sleep(randint(1,2))

        soup = BeautifulSoup(driver.page_source, "html.parser")
        store=soup.find_all('a', class_='store-details-link')
        for j in store:

            ul=u+j['href']
            print()
            print(ul)

            driver.get(ul)
            time.sleep(randint(2,4))

            try:
                element = WebDriverWait(driver, 20).until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, ".store-page-details")))
                time.sleep(randint(1,2))
            except:
                continue

            soup = BeautifulSoup(driver.page_source, "html.parser")
            div = soup.find('div',class_='store-page-details')
            try:
              loc = div.find('h1').text
              if "closed" in loc.lower():
                continue
            except:
               continue
            ph=div.find('p',class_='store-page-details-phone').text.strip()
            addr=div.find('p',class_='store-page-details-address').text.strip().split("\n")
            #print(addr)
            if len(addr) ==2:
                street=addr[0]
                addr=addr[1].strip().split(',')
            elif len(addr)>2:
                add=addr[-1]
                del addr[-1]
                street=" ".join(addr)
                addr=add.strip().split(',')
            
            cty=addr[0]
            addr=addr[1].strip().split(' ')
            sts=addr[0]
            zcode=addr[1]

            got_hours = False
            try:
                hours=soup.find('div',class_='store-page-details-hours-mobile visible-sm visible-md ui-accordion ui-widget ui-helper-reset').text
                got_hours = True
            except:
                try:
                    hours=soup.find('div',class_='store-page-details-hours-mobile visible-sm visible-md').text
                    got_hours = True
                except:
                    pass

            if got_hours: 
                hours=hours.strip().replace('\n\n','').replace('\n','')
                for day in ['MON','TUE','THU','WED','FRI','SAT','SUN']:
                    if day not in hours:
                        hours=hours.replace('TODAY',day)
            else:
                hours = '<MISSING>'

            lat,long=re.findall(r'center=([\d\.]+),([\-\d\.]+)',soup.find('div',class_='store-page-map mapViewstoredetail').find('img').get('src'))[0]

            data.append([
                    'https://www.petsmart.com/',
                     ul.replace(u'\u2019',''),
                    loc.replace(u'\u2019','').strip(),
                    street.replace(u'\u2019',''),
                    cty.replace(u'\u2019',''),
                    sts.replace(u'\u2019',''),
                    zcode.replace(u'\u2019',''),
                    'US'.replace(u'\u2019',''),
                    j['id'].replace(u'\u2019',''),
                    ph.replace(u'\u2019',''),
                    '<MISSING>',
                    lat,
                    long,
                    hours.replace(u'\u2019','')
                    ])
    
    try:
        driver.close()
    except:
        pass

    return data
    
def scrape():
    data = fetch_data()
    write_output(data)

scrape()
