from sgscrape.simple_scraper_pipeline import *
from sgscrape import simple_network_utils as net_utils
from sgscrape import simple_utils as utils
import json
from sglogging import sglog
from sgselenium import SgFirefox, SgSelenium
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time



def fetch_data():

    url = "https://www.friendlysrestaurants.com/locate/"

    
    logzilla = sglog.SgLogSetup().get_logger(logger_name='Crawler')
    son = []
    logzilla.info(f'Initializing geckodriver')
    with SgFirefox() as driver:
        logzilla.info(f'Getting page')
        driver.get(url)
        logzilla.info(f'Waiting for page to load')
        request = driver.wait_for_request('https://maps.google.com/maps-api-v3/api/js/43/1a/map.js')
        logzilla.info(f'Looking for the right request.')
        for r in driver.requests:
            if '/wp-admin/admin-ajax.php' in r.path:
                data = r.response.body
                if 'wpid' in str(data):
                    data = json.loads(data)
                    for i in data:
                        yield i
                    
                
                
  
    logzilla.info(f'Finished grabbing data!!')

def pretty_hours(k):
    return '; '.join([': '.join([i[0],str(str(i[1][0])+'-'+str(i[1][1]))]) for i in k.items()]).replace('CLOSED-CLOSED','Closed')

def scrape():
    url="https://www.friendlysrestaurants.com"
    field_defs = SimpleScraperPipeline.field_definitions(
        locator_domain = ConstantField(url),
        page_url=MappingField(mapping=['page'], value_transform = lambda x : x.replace('&#038;','&')),
        location_name=MappingField(mapping=['title']),
        latitude=MappingField(mapping=['lat']),
        longitude=MappingField(mapping=['lng']),
        street_address=MappingField(mapping=['street']),
        city=MappingField(mapping=['city']),
        state=MappingField(mapping=['state']),
        zipcode=MappingField(mapping=['zip']),
        country_code=MissingField(),
        phone=MappingField(mapping=['phone']),
        store_number=MappingField(mapping=['id']),
        hours_of_operation=MappingField(mapping=['store_hours'], raw_value_transform = pretty_hours),
        location_type=MappingField(mapping=['type'], is_required = False)
    )

    pipeline = SimpleScraperPipeline(scraper_name='friendlysrestaurants.com',
                                     data_fetcher=fetch_data,
                                     field_definitions=field_defs,
                                     log_stats_interval=15)

    pipeline.run()

if __name__ == "__main__":
    scrape()
