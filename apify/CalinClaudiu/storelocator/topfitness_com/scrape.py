from sgscrape.simple_scraper_pipeline import *
from sgscrape import simple_network_utils as net_utils
from sgscrape import simple_utils as utils
from sgrequests import SgRequests
from sglogging import sglog
from bs4 import BeautifulSoup as b4
import json

def fetch_subpage(tup):
    k = {}
    k['dex'] , k['url'] = tup
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'}
    k['hours'] = '<MISSING>'
    if k['url'] != None:
        session = SgRequests()
        son = session.get(k['url'], headers = headers)
        soup = b4(son.text, 'lxml')
        try:
            containers = soup.find_all('div',{'class':'shg-c-lg-6 shg-c-md-6 shg-c-sm-6 shg-c-xs-6'})
            days = list(containers[0].find('div').find('div').find('p').stripped_strings)
            hours = list(containers[1].find('div').find('div').find('p').stripped_strings)
            h = list(zip(days, hours))
            k['hours'] = []
            for i in h:
                k['hours'].append(i[0]+': '+i[1])
            k['hours'] = '; '.join(k['hours'])
        except:
            k['hours'] = '<MISSING>'
    return k 
    
def fetch_data():
    logzilla = sglog.SgLogSetup().get_logger(logger_name='Scraper')
    url = "https://stockist.co/api/v1/u3601/locations/search?&tag=u3601&latitude=47.805670899999996&longitude=-122.28511505&distance=99999"
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'}
    session = SgRequests()
    son = session.get(url, headers = headers).json()
    
    lize = utils.parallelize(search_space = [[dex, son['locations'][dex]['website']] for dex, i in enumerate(son['locations'])],
                fetch_results_for_rec = fetch_subpage,
                max_threads = 5,
                print_stats_interval = 5)
    for i in lize:
        store = i
        store['data'] = son['locations'][store['dex']]
        yield store


def scrape():
    url="https://www.topfitness.com/"
    field_defs = SimpleScraperPipeline.field_definitions(
        locator_domain = ConstantField(url),
        page_url=MappingField(mapping=['url']),
        location_name=MappingField(mapping=['data','name']),
        latitude=MappingField(mapping=['data','latitude']),
        longitude=MappingField(mapping=['data','longitude']),
        street_address=MultiMappingField(mapping=[['data','address_line_1'],['data','address_line_2']], part_of_record_identity = True, multi_mapping_concat_with = ', ', value_transform = lambda x : x.replace(   'None','')),
        city=MappingField(mapping=['data','city'], value_transform = lambda x : x.replace('None','<MISSING>'), part_of_record_identity = True),
        state=MappingField(mapping=['data','state'], value_transform = lambda x : x.replace('None','<MISSING>'), part_of_record_identity = True),
        zipcode=MappingField(mapping=['data','postal_code'], value_transform = lambda x : x.replace('None','<MISSING>'), is_required = False),
        country_code=MappingField(mapping=['data','country'], value_transform = lambda x : x.replace('None','<MISSING>'), is_required = False),
        phone=MappingField(mapping=['data','phone'], value_transform = lambda x : x.replace('None','<MISSING>') , is_required = False),
        store_number=MappingField(mapping=['data','id']),
        hours_of_operation=MappingField(mapping=['hours'], is_required = False),
        location_type=MappingField(mapping=['data','name'], value_transform = lambda x : '<MISSING>' if 'COMING' not in x else 'Coming Soon')
    )

    pipeline = SimpleScraperPipeline(scraper_name='topfitness.com',
                                     data_fetcher=fetch_data,
                                     field_definitions=field_defs,
                                     log_stats_interval=15)

    pipeline.run()

if __name__ == "__main__":
    scrape()
