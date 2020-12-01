from sgscrape.simple_scraper_pipeline import *
from sgscrape import simple_network_utils as net_utils
from sgscrape import simple_utils as utils
from sgrequests import SgRequests
from sglogging import sglog
from bs4 import BeautifulSoup as b4
import json

def para(tup):
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'}
    k ={}
    k['index'] = tup[0]
    k['requrl'] = tup[1]
    session = SgRequests()
    son = session.get(k['requrl'], headers = headers)
    soup = b4(son.text , 'lxml')
    try:
        k['hours'] = ' '.join(list(soup.find('dl',{'class':'available-hours','id':'available-business-hours-popover'}).stripped_strings))
    except:
        k['hours'] = '<MISSING>'

    return k
    
def fetch_data():
    logzilla = sglog.SgLogSetup().get_logger(logger_name='Scraper')
    url = "https://www.huddlehouse.com/api/olo/locations/"
    headers = {
                'User-Agent' : 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36'        }
    session = SgRequests()
    son = session.get(url, headers = headers).json()

    lize = utils.parallelize(
                search_space = [[counter,i['url']] for counter, i in enumerate(son['restaurants'])],
                fetch_results_for_rec = para,
                max_threads = 10,
                print_stats_interval = 10
                )


    
    for i in lize:
        son['restaurants'][i['index']].update(i)
        yield son['restaurants'][i['index']]
        
    logzilla.info(f'Finished grabbing data!!')

def fix_comma(x):
    h = []
    try:
        x = x.split(',')
        for i in x:
            if len(i)>1:
                h.append(i)
        h = ', '.join(h)
    except:
        h = x

    return h

def scrape():
    url="https://www.huddlehouse.com/"
    field_defs = SimpleScraperPipeline.field_definitions(
        locator_domain = ConstantField(url),
        page_url=MappingField(mapping=['url']),
        location_name=MappingField(mapping=['storename']),
        latitude=MappingField(mapping=['latitude']),
        longitude=MappingField(mapping=['longitude']),
        street_address=MappingField(mapping=['streetaddress'], value_transform = fix_comma),
        city=MappingField(mapping=['city'], value_transform = lambda x : x.replace('None','<MISSING>')),
        state=MappingField(mapping=['state'], value_transform = lambda x : x.replace('None','<MISSING>')),
        zipcode=MappingField(mapping=['zip'], value_transform = lambda x : x.replace('None','<MISSING>'), is_required = False),
        country_code=MappingField(mapping=['country']),
        phone=MappingField(mapping=['telephone'], value_transform = lambda x : x.replace('() -','<MISSING>') , is_required = False),
        store_number=MappingField(mapping=['id']),
        hours_of_operation=MappingField(mapping=['hours'], is_required = False),
        location_type=MappingField(mapping=['brand'], is_required = False)
    )

    pipeline = SimpleScraperPipeline(scraper_name='huddlehouse.com',
                                     data_fetcher=fetch_data,
                                     field_definitions=field_defs,
                                     log_stats_interval=15)

    pipeline.run()

if __name__ == "__main__":
    scrape()
