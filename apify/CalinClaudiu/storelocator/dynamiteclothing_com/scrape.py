from sgscrape.simple_scraper_pipeline import *
from sgscrape import simple_network_utils as net_utils
from sgscrape import simple_utils as utils
from sglogging import sglog
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import json

def fetch_data():
    logzilla = sglog.SgLogSetup().get_logger(logger_name='clubmonaco')
    urlUS = "https://www.dynamiteclothing.com/on/demandware.store/Sites-DynamiteGarageUS-Site/en_US/Stores-FindStores?showMap=true&radius=605300%20Mi&postalCode=96701"
    urlCA = "https://www.dynamiteclothing.com/on/demandware.store/Sites-DynamiteGarageCA-Site/en_CA/Stores-FindStores?showMap=true&radius=10000&postalCode=G0A%204V0"

    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36'
    }
    session = SgRequests()
    son = session.get(urlUS, headers = headers).json()
    for i in son['stores']:
        yield i
        
    son = session.get(urlCA, headers = headers).json()
    for i in son['stores']:
        yield i
    logzilla.info(f'Finished grabbing data!!')

def fix_hours(x):
    x = x.replace('\n\n\n\n','; ')
    x = x.replace('<div class=\"store-day\">','')
    x = x.replace('</div>\n','')
    x = x.replace('<div class=\"store-time\">',': ')
    x = x.replace('\n','')
    x = x.replace('</div>','')
    #x = x.replace('','')
    return x


def scrape():
    url="https://dynamiteclothing.com/"
    field_defs = SimpleScraperPipeline.field_definitions(
        locator_domain = ConstantField(url),
        page_url=MissingField(),
        location_name=MappingField(mapping=['name']),
        latitude=MappingField(mapping=['latitude']),
        longitude=MappingField(mapping=['longitude']),
        street_address=MultiMappingField(mapping=[['address1'],['address2']], multi_mapping_concat_with = ', '),
        city=MappingField(mapping=['city']),
        state=MappingField(mapping=['stateCode']),
        zipcode=MappingField(mapping=['postalCode']),
        country_code=MappingField(mapping=['countryCode']),
        phone=MappingField(mapping=['phone']),
        store_number=MappingField(mapping=['ID']),
        hours_of_operation=MappingField(mapping=['storeHours'], value_transform = fix_hours, is_required = False),
        location_type=MappingField(mapping=['brand'])
    )

    pipeline = SimpleScraperPipeline(scraper_name='dynamiteclothing.com',
                                     data_fetcher=fetch_data,
                                     field_definitions=field_defs,
                                     log_stats_interval=25)

    pipeline.run()

if __name__ == "__main__":
    scrape()
