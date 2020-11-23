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

    data = soup.find('div',{'class': lambda x : x and 'store__body' in x and 'pge__content' in x})
    
    k = {}

    k['CustomUrl'] = url

    try:
        k['Latitude'] = data.find('button',{'class':'store__map-container'})['style'].split(')/')[1].split(',')[1]
    except:
        k['Latitude'] = '<MISSING>'
        
    try:
        k['Longitude'] = data.find('button',{'class':'store__map-container'})['style'].split(')/')[1].split(',')[0]
    except:
        k['Longitude'] = '<MISSING>'
        
    k['Name'] = '<MISSING>'
        
    try:
        k['Address'] = data.find('p',{'class':'store__box-p'}).text.strip()
    except:
        k['Address'] = '<MISSING>'

        
    try:
        k['City'] = k['Address'].split(',')[-2]
    except:
        k['City'] = '<MISSING>'
        
    try:
        k['State'] = k['Address'].split(',')[-1].strip()
        k['State'] = k['State'].split(' ')[0]
    except:
        k['State'] = '<MISSING>'
        
    try:
        k['Zip'] = k['Address'].split(',')[-1].strip()
        k['Zip'] = k['Zip'].split(' ')[1]
    except:
        k['Zip'] = '<MISSING>'
        
    try:
        k['Phone'] = data.find('div',{'class':lambda x : x and 'store__box--phone' in x}).find('p',{'class':'store__box-p'}).text.strip()
    except:
        k['Phone'] = '<MISSING>'
        
    try:
        h = list(data.find('div',{'class':'store__box-hours-group'}).stripped_strings)
        k['OpenHours'] = '; '.join(h)
    except:
        k['OpenHours'] = '<MISSING>'

    try:
        k['Address'] = ', '.join(k['Address'].split(',')[:-2])
    except:
        k['Address'] = '<MISSING>'
            
    k['IsActive'] = '<MISSING>'      
    k['Country'] = '<MISSING>'
        
    return k

def fetch_data():
    logzilla = sglog.SgLogSetup().get_logger(logger_name='Scraper')
    url = "https://www.jetspizza.com/stores/"
    headers = {
                'User-Agent' : 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36' }
    session = SgRequests()
    son = session.get(url, headers = headers)
    soup = b4 (son.text, 'lxml')
    states = []
    stores = []


    logzilla.info(f'Grabbing state links')
    for i in soup.find('div',{'class':'pge-find-store__states'}).find_all('a',{'class':'pge-find-store__state-item'}):
            states.append(i['href'])
            
    url = 'https://locations.tacojohns.com/'
    logzilla.info(f'Grabbing store links')
    
    for i in states:
        son = session.get(i, headers = headers)
        soup = b4(son.text, 'lxml')
        links = soup.find('div',{'class':'pge-find-store__entries'})
        for j in links.find_all('a',{'class':'locator-results__store-detail'}):
            stores.append(j['href'])


    logzilla.info(f'Grabbing store data')
    
    lize = utils.parallelize(
                search_space = stores,
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
    url="https://www.tacojohns.com/"
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

    pipeline = SimpleScraperPipeline(scraper_name='tacojohns.com',
                                     data_fetcher=fetch_data,
                                     field_definitions=field_defs,
                                     log_stats_interval=15)

    pipeline.run()

if __name__ == "__main__":
    scrape()
