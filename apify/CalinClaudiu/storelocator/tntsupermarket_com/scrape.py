from sgscrape.simple_scraper_pipeline import *
from sgscrape import simple_network_utils as net_utils
from sgscrape import simple_utils as utils
from sgrequests import SgRequests
from sglogging import sglog
import json

def para(k):
    session = SgRequests()
    # https://www.tntsupermarket.com/rest/V1/xmapi/get-store-details?lang=en&id=2479
    backup = k
    ide = k['id']
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'}
    k = session.get('https://www.tntsupermarket.com/rest/V1/xmapi/get-store-details?lang=en&id='+k['id'], headers=headers).json()
    k = k['data']
    
    try:
        k['zip'] = k['address'].rsplit('.',1)[1]
        k['zip'] = k['zip'].strip()
    except:
        k['zip'] = "<MISSING>"
    
    try:
        k['region'] = k['address'].rsplit('.',1)[0].rsplit(',',1)[1]
        k['region'] = k['region'].strip()
    except:
        k['region'] = "<MISSING>"
    
    try:
        k['town'] = k['address'].split('  ',1)[1].split(',')[0]
        k['town'] = k['town'].strip()
    except:
        k['town'] = "<MISSING>"
    
    try:
        k['address'] =  k['address'].split('  ',1)[0]
    except:
        k['address'] = "<MISSING>"

    if k['town'] == "<MISSING>":
        try:
            k['address'] = k['address'].split('North Waterloo',1)[0]
            k['town'] = 'Waterloo'
        except:
            pass
    k['id'] = ide
    k['page_url'] = 'https://www.tntsupermarket.com/rest/V1/xmapi/get-store-details?lang=en&id='+k['id']
    return k

def fix_hours(x):
    x = x.replace('<br />',': ')
    
    return x
                           
def fetch_data():
    logzilla = sglog.SgLogSetup().get_logger(logger_name='Scraper')
    url = "https://www.tntsupermarket.com/rest/V1/xmapi/get-store-list-new?lang=en&address=Thornhill%2C%2BON%2C%2BL3T"
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'}
    session = SgRequests()
    son = session.get(url, headers = headers).json()
    son = son['data']['filter_by_location']['city_stores']
    copy = []
    for i in son:
        for store in i:
            copy.append(store)

    son = copy
    
    lize = utils.parallelize(
                search_space = son,
                fetch_results_for_rec = para,
                max_threads = 20,
                print_stats_interval = 20
                )
    for i in lize:
        yield i



def scrape():
    url = "https://www.tntsupermarket.com/"
    field_defs = SimpleScraperPipeline.field_definitions(
        locator_domain = ConstantField(url),
        page_url=MappingField(mapping=['page_url']),
        location_name=MappingField(mapping=['name']),
        latitude=MappingField(mapping=['lat']),
        longitude=MappingField(mapping=['lng']),
        street_address=MappingField(mapping=['address']),
        city=MappingField(mapping=['town']),
        state=MappingField(mapping=['region']),
        zipcode=MappingField(mapping=['zip']),
        country_code=MissingField(),
        phone=MappingField(mapping=['phone']),
        store_number=MappingField(mapping=['id'], part_of_record_identity = True),
        hours_of_operation=MappingField(mapping=['store_hours'], value_transform = fix_hours),
        location_type=MissingField()
    )

    pipeline = SimpleScraperPipeline(scraper_name='Loblaws Family',
                                     data_fetcher=fetch_data,
                                     field_definitions=field_defs,
                                     log_stats_interval=15)

    pipeline.run()

if __name__ == "__main__":
    scrape()
