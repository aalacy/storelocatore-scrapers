from sgscrape.simple_scraper_pipeline import *
from sgscrape import simple_network_utils as net_utils
from sgscrape import simple_utils as utils
from sgrequests import SgRequests
from sglogging import sglog
from bs4 import BeautifulSoup as b4
import json

def para(url):


    headers = {
                'User-Agent' : 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36'        }
    session = SgRequests()
    son = session.get(url, headers = headers)
    soup = b4(son.text , 'lxml')
    son = json.loads(soup.find('script',{'type':'application/ld+json'}).text)[0]
    return son

def storepara(url):
    headers = {
                'User-Agent' : 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36'        }
    session = SgRequests()
    son = session.get(url, headers = headers)
    soup = b4(son.text,'lxml')
    data = soup.find_all('div',{'class':lambda x : x and all(j in x for j in ['map-list-item-wrap','js-map-list-item'])})
    links = []
    for j in data:
        links.append(j.find('span',{'class':'loc-name'}).find('a')['href'])

    return links
                
    
def fetch_data():
    para('https://stores.shoecarnival.com/pr/aguadilla/shoe-store-aguadilla-pr-468.html')
    logzilla = sglog.SgLogSetup().get_logger(logger_name='Scraper')
    url = "https://stores.shoecarnival.com/"
    headers = {
                'User-Agent' : 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36'        }
    session = SgRequests()
    son = session.get(url, headers = headers)
    soup = b4 (son.text, 'lxml')
    states = []
    cities = []
    stores = []


    logzilla.info(f'Grabbing state links')
    for i in soup.find_all('a',{'class':lambda x : x and x.startswith('secondary-link')}):
        count = i['href'].count('/')
        if count == 4:
            states.append(i['href'])
        elif count == 5:
            cities.append(i['href'])
        elif count > 5:
            stores.append(i['href'])
            
    logzilla.info(f'Grabbing city links')
    for i in states:
        son = session.get(i, headers = headers)
        logzilla.info(f'Grabbing Links for state: {i.split("/")[-2]}')
        soup = b4(son.text, 'lxml')
        for j in soup.find('div',{'class':lambda x : x and x.startswith('map-list')}).find_all('a',{'class':'js-ga-track'}):            
            count = j['href'].count('/')
            if count == 4:
                cities.append(j['href'])
            elif count >4:
                stores.append(j['href'])

    #Not entirely necessary here:\\    for i in cities:\\        son = session.get(url+i, headers = headers)\\        soup = b4(son.text, 'lxml')\\        for j in soup.find('',{'class':lambda x : x and x.startswith('directory-container')}).find_all('a',{'class':lambda x : x and x.startswith('c-location-grid-item-link'),'href':True,'title':True,'data-yext-tracked':True}):\\            stores.append(j['href'])
    
        
            
    lize = utils.parallelize(
                search_space = stores,
                fetch_results_for_rec = storepara,
                max_threads = 15,
                print_stats_interval = 15
                )
    
    identities = set()
    links = []
    for req in lize:
        for link in req:
            if link not in identities:
                identities.add(link)
                links.append(link)

    
    lize = utils.parallelize(
                search_space = links,
                fetch_results_for_rec = para,
                max_threads = 10,
                print_stats_interval = 10
                )

    for i in lize:
        yield i
        
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
    url="https://www.shoecarnival.com/"
    field_defs = SimpleScraperPipeline.field_definitions(
        locator_domain = ConstantField(url),
        page_url=MappingField(mapping=['url']),
        location_name=MappingField(mapping=['name']),
        latitude=MappingField(mapping=['geo','latitude']),
        longitude=MappingField(mapping=['geo','longitude']),
        street_address=MappingField(mapping=['address','streetAddress'], value_transform = fix_comma),
        city=MappingField(mapping=['address','addressLocality'], value_transform = lambda x : x.replace('None','<MISSING>')),
        state=MappingField(mapping=['address','addressRegion'], value_transform = lambda x : x.replace('None','<MISSING>')),
        zipcode=MappingField(mapping=['address','postalCode'], value_transform = lambda x : x.replace('None','<MISSING>'), is_required = False),
        country_code=MissingField(),
        phone=MappingField(mapping=['address','telephone'], value_transform = lambda x : x.replace('None','<MISSING>') , is_required = False),
        store_number=MissingField(),
        hours_of_operation=MappingField(mapping=['openingHours'], is_required = False),
        location_type=MappingField(mapping=['@type']),
    )

    pipeline = SimpleScraperPipeline(scraper_name='shoecarnival.com',
                                     data_fetcher=fetch_data,
                                     field_definitions=field_defs,
                                     log_stats_interval=15)

    pipeline.run()

if __name__ == "__main__":
    scrape()
