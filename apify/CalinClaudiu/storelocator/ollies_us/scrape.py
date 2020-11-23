from sgscrape.simple_scraper_pipeline import *
from sgscrape import simple_network_utils as net_utils
from sgscrape import simple_utils as utils
from sgrequests import SgRequests
from sglogging import sglog
import json

def fetch_data():
    logzilla = sglog.SgLogSetup().get_logger(logger_name='Scraper')
    url = "https://www.ollies.us/admin/locations/ajax.aspx?Page=1&PageSize=50000&Longitude=-74.00597&Latitude=40.71427&City=&State=&F=GetNearestLocations&RangeInMiles=5000"
    headers = {
                'User-Agent' : 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36'        }
    session = SgRequests()
    son = session.post(url, headers = headers).json()

    for i in son['Locations']:
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

    return h

def scrape():
    url="https://www.ollies.us/"
    field_defs = SimpleScraperPipeline.field_definitions(
        locator_domain = ConstantField(url),
        page_url=MappingField(mapping=['CustomUrl'], value_transform = lambda x : 'https://www.ollies.us' + x),
        location_name=MappingField(mapping=['Name'], value_transform = lambda x : x.replace('None','<MISSING>')),
        latitude=MappingField(mapping=['Latitude']),
        longitude=MappingField(mapping=['Longitude']),
        street_address=MultiMappingField(mapping=[['Address1'],['Address2']], multi_mapping_concat_with = ', ', value_transform = fix_comma),
        city=MappingField(mapping=['City'], value_transform = lambda x : x.replace('None','<MISSING>')),
        state=MappingField(mapping=['State'], value_transform = lambda x : x.replace('None','<MISSING>')),
        zipcode=MappingField(mapping=['Zip'], value_transform = lambda x : x.replace('None','<MISSING>'), is_required = False),
        country_code=MissingField(),
        phone=MappingField(mapping=['Phone'], value_transform = lambda x : x.replace('None','<MISSING>') , is_required = False),
        store_number=MappingField(mapping=['StoreCode']),
        hours_of_operation=MappingField(mapping=['OpenHours'], value_transform = lambda x : x.replace('<br />','; '), is_required = False),
        location_type=MappingField(mapping=['IsActive'], value_transform = lambda x : 'Possibly Closed' if x == True else '<MISSING>' , is_required = False)
    )

    pipeline = SimpleScraperPipeline(scraper_name='ollies.us',
                                     data_fetcher=fetch_data,
                                     field_definitions=field_defs,
                                     log_stats_interval=15)

    pipeline.run()

if __name__ == "__main__":
    scrape()
