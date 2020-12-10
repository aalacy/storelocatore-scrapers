from sgscrape.simple_scraper_pipeline import *
from sgscrape import simple_network_utils as net_utils
from sgscrape import simple_utils as utils
from sglogging import sglog
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import json

def parse_store(x):
    k = {}
    try:
        k['url'] = x.find('a',{'href':lambda x : x and x.startswith('/')})['href']
    except:
        k['url']= '<MISSING>'
    
    try:
        k['name'] = x.find('h1',{'class':'mx-3 text-white font-semibold text-xl'}).text
    except:
        k['name'] = '<MISSING>'
        
    try:
        k['hours'] = x.find('div',{'class':'h-4 mx-3 text-white font-semibold text-sm'}).text
    except:
        k['hours'] = '<MISSING>'

    try:
        data = [list(i.stripped_strings) for i in x.find_all('p',{'class':'text-lg font-semibold'})]
    except:
        data = ''

        
    try:
        k['address']=data[0][0]
    except:
        k['address']='<MISSING>'
        
    try:
        k['city']=data[0][1].split(',')[0]
    except:
        k['city']='<MISSING>'
        
    try:
        k['province'] = data[0][1].split(',')[1].strip()
        k['province'] = k['province'].split(' ')[0]
    except:
        k['province']='<MISSING>'
        
    try:
        k['postalCode']= data[0][1].split(',')[1].strip()
        k['postalCode'] = k['postalCode'].split(' ')[-1]
    except:
        k['postalCode']='<MISSING>'
        
    try:
        k['phone']=data[1][1]
    except:
        k['phone']='<MISSING>'

    if k['hours'] == '':
        k['hours'] = '<MISSING>'
    k['country'] = 'US'
    return k

def fetch_data():
    #
    logzilla = sglog.SgLogSetup().get_logger(logger_name='flagshipcinemas')
    url = "https://flagshipcinemas.com/"
    #there's a chance this may change in the future.
    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36'
    }
    session = SgRequests()
    son = session.get(url, headers = headers)
    soup = BeautifulSoup(son.text, 'lxml')
    storse = soup.find('div',{'class':'px-8'})
    for i in storse.find_all('div',{'class':'max-w-screen-xs sm:max-w-none sm:w-1/2 xl:w-1/3 sm:mx-0 mx-auto py-4 sm:p-4 overflow-hidden'}):
        yield parse_store(i)
    logzilla.info(f'Finished grabbing data!!')


def scrape():
    url="https://flagshipcinemas.com"
    field_defs = SimpleScraperPipeline.field_definitions(
        locator_domain = ConstantField(url),
        page_url=MappingField(mapping=['url'], value_transform = lambda x : url+x),
        location_name=MappingField(mapping=['name']),
        latitude=MissingField(),
        longitude=MissingField(),
        street_address=MappingField(mapping=['address']),
        city=MappingField(mapping=['city'], is_required = False),
        state=MappingField(mapping=['province'], is_required = False),
        zipcode=MappingField(mapping=['postalCode'], is_required = False),
        country_code=MappingField(mapping=['country']),
        phone=MappingField(mapping=['phone'], is_required = False),
        store_number=MissingField(),
        hours_of_operation=MappingField(mapping=['hours'], is_required = False),
        location_type=MissingField()
    )

    pipeline = SimpleScraperPipeline(scraper_name='flagshipcinemas.com',
                                     data_fetcher=fetch_data,
                                     field_definitions=field_defs,
                                     log_stats_interval=25)

    pipeline.run()

if __name__ == "__main__":
    scrape()
