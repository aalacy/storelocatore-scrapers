from sgscrape.simple_scraper_pipeline import *
from sgscrape import simple_network_utils as net_utils
from sgscrape import simple_utils as utils
from sgzip import DynamicZipSearch, SearchableCountries
from sglogging import sglog
from sgselenium import SgFirefox, SgSelenium
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import json
import time

def parse_store(x):
    k = {}
    k ['error'] = False
    if len(x)<100:
        k ['error'] = True
        return k
    x = BeautifulSoup(x,'lxml')
    k['url'] = ''
    
    try:
        k['url'] = x.find('h4').find('a',{'href':True})['href']
    except:
        k['url'] = "<MISSING>"

    if(k['url'] == '') or (k['url'] == "<MISSING>"):
        try:
            k['url'] = x.find(lambda tag : tag.name == 'a' and "Location Info" in tag.text)['href']
        except:
            k['url'] = "<MISSING>"
        
    try:
        k['store'] = x.find('h4').find('a',{'href':True}).text.replace('&#8211;','-')
    except:
        k['store'] = "<MISSING>"
        
    try:
        k['lat'] = x.find('a' ,{'href': lambda x : x and x.startswith('https://www.google.com/maps/dir//')})['href'].split('dir//')[1].split('/',1)[0]
    except:
        k['lat'] = "<MISSING>"
        
    try:
        k['lng'] = k['lat'].split(',')[1]
        k['lat'] = k['lat'].split(',')[0]
    except:
        k['lng'] = "<MISSING>"
        
    try:
        k['address'] = x.find('div',{'class':'col-md-6'}).find('p').text.split(',')[0]
    except:
        k['address'] = "<MISSING>"
        
    try:
        k['city'] = k['store'].split('–')
        k['city'] = k['city'][0].strip()
        
    except:
        k['city'] = "<MISSING>"
        
    try:
        k['state'] = x.find('div',{'class':'col-md-6'}).find('p').text.split(',')
        test = k['state'][-1].strip()
        if(len(k['state']))==4 and test.isdigit():
            k['state'] = k['state'][-2]
        else:
            k['state'] = k['state'][-1].strip()
            k['state'] = k['state'].split(' ')[0]
    except:
        k['state'] = "<MISSING>"
        
    try:
        k['zip'] = x.find('div',{'class':'col-md-6'}).find('p').text.split(',')
        test = k['zip'][-1].strip()
        if(len(k['zip']))==4 and test.isdigit():
            k['zip'] = k['zip'][-1]
        else:
            k['zip'] = k['zip'][-1].strip()
            k['zip'] = k['zip'].split(' ')[1]
    except:
        k['zip'] = "<MISSING>"
        
    k['country'] = "<MISSING>"
        
    try:
        k['phone'] = x.find('a',{'class':'phoneHref','href': lambda x : x and x.startswith('tel:')})['href'].split('tel:')[-1]
    except:
        k['phone'] = "<MISSING>"

    k['id'] = "<MISSING>" 
        
    try:
        h = []
        k['description'] = x.find('ul' , {'class':'openingList firstOpening clearfix row'}).find_all('li')
        for i in k['description']:
            h.append(i.text)
        k['description'] = '; '.join(h)
        k['description'] = k['description'].replace('; ','',1)
    except:
        k['description'] = "<MISSING>"

    try:
        k['type'] = x.find('p',{'class':'extraText'}).text
        if not any(i in k['type'] for i in ['ONLY', 'SOON', 'Open!', 'TEMPORARILY']):
            k['type'] = "<MISSING>"
    except:
        k['type'] = "<MISSING>"
    if '20003' in k['state']:
        k['state'] = 'WA'
        k['zip'] = '20003'
    if 'PA' in k['zip'] and '19406' in k['zip']:
        k['address'] = k['address'] +', Ste 3045'
        k['state'] = 'PA'
        k['zip'] = '19406'
    return k

def fetch_data():
    logzilla = sglog.SgLogSetup().get_logger(logger_name='Scraper')
    logzilla.info(f'Grabbing data from ajax post request /wp-admin/admin-ajax')
    
    with SgFirefox() as driver:
        driver.get('https://bonchon.com/locations-menus/')
        
        ZipSearch = DynamicZipSearch(country_codes=[SearchableCountries.USA], max_search_results = 130)
        ZipSearch.initialize()
        postcode  = ZipSearch.next()
        identities = set()
        #Zip search is not necessarry since query returns 130 stores and entire company has only 112 locations, but it's more future-proof
        while postcode:
            search =  WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.XPATH,'//*[@id="location-search-address"]')))
            search.send_keys(str(postcode))
            search.send_keys(Keys.RETURN)
            time.sleep(2)
            locs = WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.XPATH,'//*[@id="post-7"]/div[2]/div/div[1]/div')))
            driver.execute_script("return arguments[0].scrollIntoView(true);", locs)
            more = WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.XPATH,'//*[@id="post-7"]/div[2]/div/div[2]/a/span')))
            driver.execute_script("return arguments[0].scrollIntoView(true);", more)
            more.click()
            x = ''
            for r in driver.requests:
                if '/wp-admin/admin-ajax' in r.path:
                    x = r
                    
            son = json.loads(x.response.body)
            stores = []
            stores = ['<div class=\"store-location-item\">'+i for i in son['stores'].split('<div class=\"store-location-item\">')]
            result_lats = []
            result_longs = []
            result_coords = []
            topop = 0
            if len(stores)!=0:
                for j in stores:
                    k = {}
                    k = parse_store(j)
                    if k['error'] != True:
                        result_lats.append(k['lat'])
                        result_longs.append(k['lng'])
                        if str(str(k['lat'])+str(k['lng'])) not in identities:
                            identities.add(str(str(k['lat'])+str(k['lng'])))
                            yield k
                        else:
                            topop += 1
            result_coords = list(zip(result_lats,result_longs))
            logzilla.info(f'Zipcodes remaining: {ZipSearch.zipcodes_remaining()}; Last request yields {len(result_coords)-topop} stores.')
            ZipSearch.update_with(result_coords)
            postcode = ZipSearch.next()
    logzilla.info(f'Finished grabbing data!!')

def fix_hours(x):
    x = x.replace('<p>','')
    x = x.replace('<br \/>\n','')
    x = x.replace('<\/p>\n','')
    x = x.replace('<\/p>','')
    x = x.replace('\n','')
    x = x.replace('&#8211;','-')
    x = x.replace('<br />',' ')
    x = x.replace('</p>','')
    x = x.replace('/','-')
    if len(x)<3:
        x = "<MISSING>"
    return x

def scrape():
    url="https://bonchon.com/"
    field_defs = SimpleScraperPipeline.field_definitions(
        locator_domain = ConstantField(url),
        page_url=MappingField(mapping=['url']),
        location_name=MappingField(mapping=['store']),
        latitude=MappingField(mapping=['lat']),
        longitude=MappingField(mapping=['lng']),
        street_address=MappingField(mapping=['address']),
        city=MappingField(mapping=['city']),
        state=MappingField(mapping=['state']),
        zipcode=MappingField(mapping=['zip']),
        country_code=MappingField(mapping=['country']),
        phone=MappingField(mapping=['phone']),
        store_number=MappingField(mapping=['id']),
        hours_of_operation=MappingField(mapping=['description']),
        location_type=MappingField(mapping=['type'], is_required = False)
    )

    pipeline = SimpleScraperPipeline(scraper_name='bonchon.com',
                                     data_fetcher=fetch_data,
                                     field_definitions=field_defs,
                                     log_stats_interval=25)

    pipeline.run()

if __name__ == "__main__":
    scrape()
