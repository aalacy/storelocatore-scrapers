from sgscrape.simple_scraper_pipeline import *
from sgscrape import simple_network_utils as net_utils
from sgscrape import simple_utils as utils
from sgrequests import SgRequests
from sglogging import sglog
import json


def fetch_data():
    logzilla = sglog.SgLogSetup().get_logger(logger_name='Scraper')
    url = "https://stockist.co/api/v1/u6694/locations/search?&latitude=60.727937&longitude=-135.058858&distance=5325235"
    headers = {
                'User-Agent' : 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36'}
    
    session = SgRequests()
    son = session.get(url, headers = headers).json()
    
    for i in son['locations']:
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

    return h.replace('<br>','')


def scrape():
    url="https://www.marbleslab.ca/"
    field_defs = SimpleScraperPipeline.field_definitions(
        locator_domain = ConstantField(url),
        page_url=MissingField(),
        location_name=MappingField(mapping=['name'], value_transform = lambda x : x.replace('None','<MISSING>').replace('<br>','')),
        latitude=MappingField(mapping=['latitude'], is_required = False),
        longitude=MappingField(mapping=['longitude'], is_required = False),
        street_address=MultiMappingField(mapping=[['address_line_1'],['address_line_2']],multi_mapping_concat_with = ', ', value_transform = fix_comma),
        city=MappingField(mapping=['city'], value_transform = lambda x : x.replace('None','<MISSING>')),
        state=MappingField(mapping=['state'], value_transform = lambda x : x.replace('None','<MISSING>')),
        zipcode=MappingField(mapping=['postal_code'], value_transform = lambda x : x.replace('None','<MISSING>'), is_required = False),
        country_code=MappingField(mapping=['country']),
        phone=MappingField(mapping=['phone'], value_transform = lambda x : x.replace('None','<MISSING>') , is_required = False),
        store_number=MappingField(mapping=['id']),
        hours_of_operation=MappingField(mapping=['description'], is_required = False),
        location_type=MissingField()
    )

    pipeline = SimpleScraperPipeline(scraper_name='marbleslab.ca',
                                     data_fetcher=fetch_data,
                                     field_definitions=field_defs,
                                     log_stats_interval=15)

    pipeline.run()

if __name__ == "__main__":
    scrape()
