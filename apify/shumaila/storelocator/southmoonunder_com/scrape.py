from time import sleep
import csv, re
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from selenium import webdriver
session = SgRequests()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
           }

from selenium.webdriver.chrome.options import Options
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('southmoonunder_com')


options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
driver = webdriver.Chrome("chromedriver", options = options)


def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    data = []
    p = 0
    pattern = re.compile(r'\s\s+') 
    url = 'https://www.southmoonunder.com/store-locator?dwcont=C766496694'
    logger.info(url)
    driver.get(url)
    
    driver.find_element_by_xpath('/html/body/div[1]/div/div[2]/div[1]/div/div[1]/div[2]/form/fieldset/button').click()
    sleep(5)
    divlist = driver.find_element_by_class_name('storeslocated')
    divlist = BeautifulSoup(divlist.get_attribute('innerHTML'),'html.parser')
    driver.quit()
    
    divlist = divlist.findAll('div',{'class':'storeTile'})
    for div in divlist:
        title = div.find('h2').text.lstrip().replace('\n','').rstrip()
        link = 'https://www.southmoonunder.com'+div.find('h2').find('a')['href']
        address = div.find('div',{'class':'storeaddress'}).text.splitlines()
        street = address[1]
        city,state = address[2].replace('\t','').split(', ')
        state,pcode = state.lstrip().split(' ',1)
        phone = address[4].split('\xa0')[0]        
        coord = div.find('iframe')['src'].split('!2d',1)[1].split('!2m')[0]
        longt, lat = coord.split('!3d')
        hourlist = div.find('div',{'class':'storeHours'}).findAll('li')
        hours= ''
        for hr in hourlist:
            hours = hours + hr.text +' '
        hours = re.sub(pattern,' ',hours).replace('pm',' pm').replace('am',' am')
        data.append([
                        'https://www.southmoonunder.com/',
                        link,                   
                        title,
                        street,
                        city,
                        state,
                        pcode,
                        'US',
                        '<MISSING>',
                        phone,
                        '<MISSING>',
                        lat,
                        longt,
                        hours
                    ])
        #logger.info(p,data[p])
        p += 1
                            
   
    
    
    return data


def scrape():
    data = fetch_data()
    write_output(data)
scrape()
