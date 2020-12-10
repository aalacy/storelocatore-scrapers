from sgscrape.simple_scraper_pipeline import *
from sgscrape import simple_network_utils as net_utils
from sgscrape import simple_utils as utils
from sglogging import sglog
from sgrequests import SgRequests
import json
import re

def fetch_data():
    logzilla = sglog.SgLogSetup().get_logger(logger_name='Scraper')
    url = "https://api.freshop.com/1/stores?app_key=sun_fresh"
    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36'
    }
    session = SgRequests()
    son = session.get(url, headers = headers).json()
    for i in son['items']:
        yield i
    logzilla.info(f'Finished grabbing data!!')

def nice_hours(x):
    hours = []
    x = x.split('\n')
    for i in x:
        if bool(re.search(r'\d', i)) == 1:
            hours.append(i)


    return '; '.join(hours)

def scrape():
    url="https://www.mysunfresh.com/"
    field_defs = SimpleScraperPipeline.field_definitions(
        locator_domain = ConstantField(url),
        page_url=MappingField(mapping=['url'], is_required = False),
        location_name=MappingField(mapping=['name']),
        latitude=MappingField(mapping=['latitude'], is_required = False),
        longitude=MappingField(mapping=['longitude'], is_required = False),
        street_address=MappingField(mapping=['address_1'], is_required = False),
        city=MappingField(mapping=['city'], is_required = False),
        state=MappingField(mapping=['state'], is_required = False),
        zipcode=MappingField(mapping=['postal_code'], is_required = False),
        country_code=MappingField(mapping=['timezone'], value_transform = lambda x : 'US' if 'America' in x else x , is_required = False),
        phone=MappingField(mapping=['phone'], is_required = False),
        store_number=MappingField(mapping=['id']),
        hours_of_operation=MappingField(mapping=['hours_md'], value_transform = nice_hours),
        location_type=MissingField()
    )

    pipeline = SimpleScraperPipeline(scraper_name='mysunfresh.com',
                                     data_fetcher=fetch_data,
                                     field_definitions=field_defs,
                                     log_stats_interval=25)

    pipeline.run()

if __name__ == "__main__":
    scrape()
