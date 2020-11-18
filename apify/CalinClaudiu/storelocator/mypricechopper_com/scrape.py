from sgscrape.simple_scraper_pipeline import *
from sgscrape import simple_network_utils as net_utils
from sgscrape import simple_utils as utils
from sglogging import sglog
from sgrequests import SgRequests
import bs4
from bs4 import BeautifulSoup
import json

def fetch_data():
    logzilla = sglog.SgLogSetup().get_logger(logger_name='mypricechopper')
    url = "https://mypricechopper.com/public/stores"
    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36'
    }
    session = SgRequests()
    son = session.get(url, headers = headers).json()
    for i in son['data']:
        data = session.get("https://mypricechopper.com/"+i['StoreDetailsPageUrl'], headers = headers)
        soup = BeautifulSoup(data.text , 'lxml')
        try:
            hours = soup.find('div',{'class':'card flex-fill'}).find('div',{'class':'card-body'}).find_all('div')
            k = []
            for j in hours:
                k.append(j.text)
            i['hours'] = '; '.join(k).strip()
            if len(i['hours']) < 3:
                i['hours'] = i['PharmacyHoursForWeek']
        except Exception as e:
            logzilla.info(f'Error grabbing data!! \n {e}')
            
        yield i
    logzilla.info(f'Finished grabbing data!!')

def scrape():
    url="https://mypricechopper.com/"
    field_defs = SimpleScraperPipeline.field_definitions(
        locator_domain = ConstantField(url),
        page_url=MappingField(mapping=['StoreDetailsPageUrl'], value_transform = lambda x : "https://mypricechopper.com/"+x),
        location_name=MappingField(mapping=['Landmark']),
        latitude=MappingField(mapping=['Latitude']),
        longitude=MappingField(mapping=['Longitude']),
        street_address=MappingField(mapping=['Address1']),
        city=MappingField(mapping=['City']),
        state=MappingField(mapping=['State']),
        zipcode=MappingField(mapping=['Zip']),
        country_code=MissingField(),
        phone=MappingField(mapping=['Phone']),
        store_number=MappingField(mapping=['StoreId']),
        hours_of_operation=MappingField(mapping=['PharmacyHoursForWeek'], is_required = False),
        location_type=MissingField()
    )

    pipeline = SimpleScraperPipeline(scraper_name='mypricechopper.com',
                                     data_fetcher=fetch_data,
                                     field_definitions=field_defs,
                                     log_stats_interval=25)

    pipeline.run()

if __name__ == "__main__":
    scrape()
