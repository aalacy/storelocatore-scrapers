from sgscrape.simple_scraper_pipeline import *
from sgscrape import simple_network_utils as net_utils
from sgscrape import simple_utils as utils
from sgrequests import SgRequests
from sglogging import sglog
from bs4 import BeautifulSoup as b4

def parse_store(x):
    
    k = {}
    k['id'] = x['id'].split('single-')[1]
    try:
        k['lat'] = x.find('div',{'class':lambda x : x and x.startswith('location-map')})['ng-init'].split('"lat":',1)[1]
    except:
        k['lat'] = '<MISSING>'
        
    try:
        k['lat'], k['lon'] =k['lat'].split(',"lng":',1)
        k['lon'] = k['lon'].split(',')[0]
    except:
        k['lon'] = '<MISSING>'
        
    try:
        k['name'] = x.find('h3',{'class':'location-name'}).text
    except:
        k['name'] = '<MISSING>'
        
    try:
        k['city'] = x.find('div',{'class':'location_address-2'}).text.split(',')[0]
    except:
        k['city'] = '<MISSING>'
        
    try:
        k['state'] = x.find('div',{'class':'location_address-2'}).text.split(',')[1]
    except:
        k['state'] = '<MISSING>'
        
    try:
        k['address'] = x.find('div',{'class':'location_address'}).text
    except:
        k['address'] = '<MISSING>'

    try:
        k['zip'] = x.find('div',{'class':'location-postal-code'}).text
    except:
        k['zip'] = '<MISSING>'
        
    try:
        k['phone'] = x.find('a',{'class':'address-block-phone'}).text
    except:
        k['phone'] = '<MISSING>'

    try:
        k['hours'] = list(x.find('div',{'class':lambda x : x and x.startswith('vc_col-sm-3')}).stripped_strings)
        k['hours'].pop(0)
        k['hours'] = '; '.join(k['hours'])
    except:
        k['hours'] = '<MISSING>'



    return k    

    
def fetch_data():
    logzilla = sglog.SgLogSetup().get_logger(logger_name='Scraper')
    url = "https://www.pinkberrycanada.ca/find-a-store/"
    headers = {
                'User-Agent' : 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36'        }
    session = SgRequests()
    son = session.get(url, headers = headers)
    soup = b4(son.text, 'lxml')
    stores = soup.find('div',{'id':'location-singles','style':'True'})
    stores = soup.find_all('div',{'id':lambda x : x and x.startswith('location-single-'),'class':'container location-single'})

    for i in stores:
        k = parse_store(i)
        k['requrl'] = soup.find('a',{'data-location':k['id']})['href']
        yield k

    
   
    
    logzilla.info(f'Finished grabbing data!!')

def good_phone(x):
    try:
        x = x.split('ext')[0]
    except:
        x = x
    try:
        x= x.split('int')[0]
    except:
        x = x
    x = x.replace('None','<MISSING>')
    return x


def scrape():
    url="https://www.pinkberrycanada.ca/"
    field_defs = SimpleScraperPipeline.field_definitions(
        locator_domain = ConstantField(url),
        page_url=MappingField(mapping=['requrl']),
        location_name=MappingField(mapping=['name']),
        latitude=MappingField(mapping=['lat']),
        longitude=MappingField(mapping=['lon']),
        street_address=MappingField(mapping=['address']),
        city=MappingField(mapping=['city'], value_transform = lambda x : x.replace('None','<MISSING>')),
        state=MappingField(mapping=['state'], value_transform = lambda x : x.replace('None','<MISSING>')),
        zipcode=MappingField(mapping=['zip'], value_transform = lambda x : x.replace('None','<MISSING>'), is_required = False),
        country_code=ConstantField('CA'),
        phone=MappingField(mapping=['phone'], value_transform = good_phone , is_required = False),
        store_number=MappingField(mapping=['id']),
        hours_of_operation=MappingField(mapping=['hours']),
        location_type=MissingField()
    )

    pipeline = SimpleScraperPipeline(scraper_name='pinkberrycanada.ca',
                                     data_fetcher=fetch_data,
                                     field_definitions=field_defs,
                                     log_stats_interval=15)

    pipeline.run()

if __name__ == "__main__":
    scrape()
