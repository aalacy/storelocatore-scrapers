from sgscrape.simple_scraper_pipeline import *
from sgscrape import simple_network_utils as net_utils
from sgscrape import simple_utils as utils
from sglogging import sglog
from sgselenium import SgFirefox, SgSelenium
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from bs4 import BeautifulSoup as b4
import json
import time


def parse_store(son):
    
    data = son
    days = ['M-','T-','W-','Th-','F-','Sa-','Su-','-F:','24/7','Closed','day','Mon','Tue','Wed','Thu','Fri','Sat','Sun','0am','1am','2am','3am','4am','5am','6am','7am','8am','9am','0pm','1pm','2pm','3pm','4pm','5pm','6pm','7pm','8pm','9pm']
    
    try:
        addr_data = list(data.find('div',{'class':'col-10'}).find('address').stripped_strings)
    except:
        addr_data = '<MISSING>'
    
    k = {}

    k['CustomUrl'] = '<MISSING>'

    k['Latitude'] = '<MISSING>'
        
    k['Longitude'] = '<MISSING>'
        
    try:
        k['Name'] = data.find('h6',{'class':lambda x : x and x.startswith('store-title')}).text.strip()
    except:
        k['Name'] = '<MISSING>'
        
    try:
        k['Address'] = addr_data[0]
    except:
        k['Address'] = '<MISSING>'
        
    try:
        k['City'] = addr_data[1].split(',',1)[0]
    except:
        k['City'] = '<MISSING>'
        
    try:
        k['State'] = addr_data[1].split(',',1)[1].strip()
        k['State'] = k['State'].split(' ')[0]
    except:
        k['State'] = '<MISSING>'
        
    try:
        k['Zip'] = addr_data[1].split(',',1)[1].strip()
        k['Zip'] = k['Zip'].split(' ')[-1]
    except:
        k['Zip'] = '<MISSING>'
        
    try:
        k['Phone'] = data.find('a',{'class':lambda x : x and x.startswith('store-phone')}).text.strip()
    except:
        k['Phone'] = '<MISSING>'
        
    try:
        everything = data.find_all('div')
        h = []
        for i in everything:
            if any(j in i.text for j in days) and len(i.text)>2:
                h.append(i.text.strip())

        while 'Hours' in h[0] or 'Information' in h[0] or 'preferred' in h[0] or 'Message' in h[0] or not any(i.isdigit() for i in h[0]):
            h.pop(0)
        k['OpenHours'] = '; '.join(h)
    except:
        k['OpenHours'] = '<MISSING>'
            
    k['IsActive'] = '<MISSING>'
    k['Country'] = '<MISSING>'
        
    return k


def fetch_data():
    logzilla = sglog.SgLogSetup().get_logger(logger_name='Scraper')
    url = "https://groceryoutlet.com/store-locator"
    
    son = ''
    with SgFirefox() as driver:
        logzilla.info(f'Getting page..')
        driver.get(url)
        logzilla.info(f'Waiting for response to load.')
        results = WebDriverWait(driver, 40).until(EC.visibility_of_element_located((By.CSS_SELECTOR,'#main > div > div.section.section-page.section-page-store-locator.my-50.my-md-100 > form > div.col-lg-4.results.store-locator-results.order-12.order-lg-1')))
        driver.execute_script("return arguments[0].scrollIntoView(true);", results)
        elm = WebDriverWait(driver, 40).until(EC.visibility_of_element_located((By.CSS_SELECTOR,'#main > div > div.section.section-page.section-page-store-locator.my-50.my-md-100 > form > div.col-lg-8.map.order-1.order-lg-12 > div > div > div > div:nth-child(12) > div > div:nth-child(3) > div > button:nth-child(3)')))
        driver.execute_script("return arguments[0].scrollIntoView(true);", elm)
        scroll = WebDriverWait(driver, 40).until(EC.visibility_of_element_located((By.CSS_SELECTOR,'#footer > div.sign-up-banner.show > div > div > button.close-banner.close-modal')))
        driver.execute_script("arguments[0].click();", scroll)
        driver.execute_script("return arguments[0].scrollIntoView(true);", scroll)
        driver.execute_script("return arguments[0].scrollIntoView(true);", elm)
        for i in range(10):
            driver.execute_script("arguments[0].click();", elm)
            time.sleep(1)
            
        logzilla.info(f'Waiting for locations to load.')
        time.sleep(10)
        soup = b4(driver.page_source, 'lxml')
        stores = soup.find('ul',{'class':lambda x : x and x.startswith('result-item-list')})
        
        for i in stores.find_all('li',{'class':lambda x : x and x.startswith('border-bottom my-4'),'data-store-number':True}):
            k = parse_store(i)
            yield k
    
    


        
    logzilla.info(f'Finished grabbing data!!')

def fix_comma(x):
    h = []
    
    x = x.replace('None','')
    try:
        x = x.split(',')
        for i in x:
            if len(i)>1:
                h.append(i)
        h = ', '.join(h)
    except:
        h = x

    if(len(h)<2):
        h = '<MISSING>'
    
    return h


def scrape():
    url="https://www.groceryoutlet.com/"
    field_defs = SimpleScraperPipeline.field_definitions(
        locator_domain = ConstantField(url),
        page_url=MappingField(mapping=['CustomUrl']),
        location_name=MappingField(mapping=['Name'], value_transform = lambda x : x.replace('None','<MISSING>')),
        latitude=MappingField(mapping=['Latitude']),
        longitude=MappingField(mapping=['Longitude']),
        street_address=MappingField(mapping=['Address'], value_transform = fix_comma),
        city=MappingField(mapping=['City'], value_transform = lambda x : x.replace('None','<MISSING>')),
        state=MappingField(mapping=['State'], value_transform = lambda x : x.replace('None','<MISSING>')),
        zipcode=MappingField(mapping=['Zip'], value_transform = lambda x : x.replace('None','<MISSING>'), is_required = False),
        country_code=MappingField(mapping=['Country']),
        phone=MappingField(mapping=['Phone'], value_transform = lambda x : x.replace('None','<MISSING>') , is_required = False),
        store_number=MissingField(),
        hours_of_operation=MappingField(mapping=['OpenHours'], is_required = False),
        location_type=MappingField(mapping=['IsActive']),
    )

    pipeline = SimpleScraperPipeline(scraper_name='groceryoutlet.com',
                                     data_fetcher=fetch_data,
                                     field_definitions=field_defs,
                                     log_stats_interval=15)

    pipeline.run()

if __name__ == "__main__":
    scrape()
