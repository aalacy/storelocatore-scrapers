from sgscrape.simple_scraper_pipeline import *
from sgscrape import simple_network_utils as net_utils
from sgscrape import simple_utils as utils
from sglogging import sglog
from sgrequests import SgRequests
import json

def fetch_data():
    logzilla = sglog.SgLogSetup().get_logger(logger_name='merrymaidscanad')
    url = "https://merrymaids.ca/getstores_new.php"
    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36'
    }
    session = SgRequests()
    son = session.get(url, headers = headers).json()
    for i in son:
        yield i
    logzilla.info(f'Finished grabbing data!!')

def nice_hours(x):
    hours = []
    if x != None:
        for i in x:
            hours.append(i['DayOfWeek']+': '+i['Hours'])
    else:
        hours.append('<MISSING>')
    return '; '.join(hours)

def scrape():
    url="https://merrymaids.ca/"
    field_defs = SimpleScraperPipeline.field_definitions(
        locator_domain = ConstantField(url),
        page_url=MappingField(mapping=['website'], value_transform = lambda x : x if 'http' in x else url+x),
        location_name=MappingField(mapping=['name']),
        latitude=MappingField(mapping=['lat']),
        longitude=MappingField(mapping=['lng']),
        street_address=MappingField(mapping=['address']),
        city=MappingField(mapping=['city'], is_required = False),
        state=MappingField(mapping=['province']),
        zipcode=MappingField(mapping=['postalCode']),
        country_code=MappingField(mapping=['country']),
        phone=MappingField(mapping=['phone']),
        store_number=MappingField(mapping=['id']),
        hours_of_operation=MissingField(),
        location_type=MappingField(mapping=['status'], value_transform = lambda x : "<MISSING>" if x == 'Active' else x)
    )

    pipeline = SimpleScraperPipeline(scraper_name='merrymaids.ca',
                                     data_fetcher=fetch_data,
                                     field_definitions=field_defs,
                                     log_stats_interval=25)

    pipeline.run()

if __name__ == "__main__":
    scrape()
