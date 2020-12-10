from sgscrape.simple_scraper_pipeline import *
from sgscrape import simple_network_utils as net_utils
from sgscrape import simple_utils as utils
from sglogging import sglog
from sgrequests import SgRequests
import json

def fetch_data():
    logzilla = sglog.SgLogSetup().get_logger(logger_name='checkmate')
    urlCA = "https://www.garageclothing.com/on/demandware.store/Sites-DynamiteGarageCA-Site/en_CA/Stores-FindStores?showMap=true&radius=50000&postalCode="
    urlUSA = "https://www.garageclothing.com/on/demandware.store/Sites-DynamiteGarageUS-Site/en_US/Stores-FindStores?showMap=true&radius=5000&postalCode="
    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36'
    }
    session = SgRequests()
    son = session.get(urlCA, headers = headers).json()
    logzilla.info(f"Grabbing {len(son['stores'])} stores from CA")
    for i in son['stores']:
        yield i
    son = session.get(urlUSA, headers = headers).json()
    logzilla.info(f"Grabbing {len(son['stores'])} stores from USA")
    for i in son['stores']:
        yield i
    
    logzilla.info(f'Finished grabbing data!!')

def fix_hours(x):
    x = x.replace('</div>\n\n','; ')
    x = x.replace('<div class=\"store-time\">','')
    x = x.replace('<div class=\"store-day\">','')
    x = x.replace('</div>\n',': ')
    x = x.replace('\n','')
    x = x.replace('</div>','')
    if len(x)<3:
        x = "<MISSING>"
    return x

def scrape():
    url="https://garageclothing.com/"
    field_defs = SimpleScraperPipeline.field_definitions(
        locator_domain = ConstantField(url),
        page_url=MissingField(),
        location_name=MappingField(mapping=['name']),
        latitude=MappingField(mapping=['latitude']),
        longitude=MappingField(mapping=['longitude']),
        street_address=MultiMappingField(mapping=[['address1'],['address2']], multi_mapping_concat_with = ', ', value_transform = lambda x : x.replace(', None','')),
        city=MappingField(mapping=['city']),
        state=MappingField(mapping=['stateCode']),
        zipcode=MappingField(mapping=['postalCode']),
        country_code=MappingField(mapping=['countryCode']),
        phone=MappingField(mapping=['phone']),
        store_number=MappingField(mapping=['ID']),
        hours_of_operation=MappingField(mapping=['storeHours'], value_transform = fix_hours, is_required = False),
        location_type=MappingField(mapping=['brand'])
    )

    pipeline = SimpleScraperPipeline(scraper_name='garageclothing.com',
                                     data_fetcher=fetch_data,
                                     field_definitions=field_defs,
                                     log_stats_interval=25)

    pipeline.run()

if __name__ == "__main__":
    scrape()
