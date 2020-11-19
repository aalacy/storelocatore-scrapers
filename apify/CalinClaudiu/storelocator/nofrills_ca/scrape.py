from sgscrape.simple_scraper_pipeline import *
from sgscrape import simple_network_utils as net_utils
from sgscrape import simple_utils as utils
from sgrequests import SgRequests
from sglogging import sglog
import json

def fetch_data():
    logzilla = sglog.SgLogSetup().get_logger(logger_name='Scraper')
    url = "https://www.loblaws.ca/api/pickup-locations?"
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'}
    session = SgRequests()
    son = session.get(url, headers = headers).json()
    for i in son:
        yield i



def scrape():
    url="https://www.nofrills.ca/"
    field_defs = SimpleScraperPipeline.field_definitions(
        locator_domain = ConstantField(url),
        page_url=MappingField(mapping=['storeId'], value_transform = lambda x : 'https://www.nofrills.ca/store-locator/details/'+x),
        location_name=MappingField(mapping=['name']),
        latitude=MappingField(mapping=['geoPoint','latitude']),
        longitude=MappingField(mapping=['geoPoint','longitude']),
        street_address=MultiMappingField(mapping=[['address','line1'],['address','line2']], part_of_record_identity = True, multi_mapping_concat_with = ', ', value_transform = lambda x : x.replace(   'None','')),
        city=MappingField(mapping=['address','town'], value_transform = lambda x : x.replace('None','<MISSING>'), part_of_record_identity = True),
        state=MappingField(mapping=['address','region'], value_transform = lambda x : x.replace('None','<MISSING>'), part_of_record_identity = True),
        zipcode=MappingField(mapping=['address','postalCode'], value_transform = lambda x : x.replace('None','<MISSING>'), is_required = False),
        country_code=MappingField(mapping=['address','country'], value_transform = lambda x : x.replace('None','<MISSING>')),
        phone=MappingField(mapping=['contactNumber'], value_transform = lambda x : x.replace('None','<MISSING>') , is_required = False),
        store_number=MappingField(mapping=['storeId']),
        hours_of_operation=MappingField(mapping=['openNowResponseData','hours'], value_transform = lambda x : x.replace('None','<MISSING>')),
        location_type=MappingField(mapping=['storeBannerId'])
    )

    pipeline = SimpleScraperPipeline(scraper_name='nofrills.ca',
                                     data_fetcher=fetch_data,
                                     field_definitions=field_defs,
                                     log_stats_interval=15)

    pipeline.run()

if __name__ == "__main__":
    scrape()
