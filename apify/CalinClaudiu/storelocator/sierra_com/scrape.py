from sgscrape.simple_scraper_pipeline import *
from sgscrape import simple_network_utils as net_utils
from sgscrape import simple_utils as utils
from sgrequests import SgRequests
from sglogging import sglog
import sgzip
from sgzip import DynamicGeoSearch, SearchableCountries
import json

def parse_store(k):
    k['error'] = False
    k['page_url'] = '<INACCESSIBLE>'
    return k    
    
def fetch_data():
    logzilla = sglog.SgLogSetup().get_logger(logger_name='Scraper')
    url = "https://mktsvc.tjx.com/storelocator/GetSearchResults?geolat=37.09024&geolong=-95.712891&chain=8&maxstores=10000&radius=10000"
    headers = {
                'User-Agent' : 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36'        }
    session = SgRequests()
    son = session.get(url, headers = headers).json()
    search = sgzip.DynamicGeoSearch(country_codes=[SearchableCountries.USA])
    search.initialize()
    coord = search.next()
    identities = set()
    while coord:
        lat, long = coord
        son = session.get('https://mktsvc.tjx.com/storelocator/GetSearchResults?geolat='+str(lat)+'&geolong='+str(long)+'&chain=50&maxstores=10000&radius=10000', headers = headers).json()
        result_lats = []
        result_longs = []
        result_coords = []
        topop = 0
        stores = son['Stores']
        if len(stores)!=0:
            for j in stores:
                k = {}
                k = parse_store(j)
                if k['error'] != True:
                    result_lats.append(k['Latitude'])
                    result_longs.append(k['Longitude'])
                    if str(str(k['Latitude'])+str(k['Longitude'])) not in identities:
                        identities.add(str(str(k['Latitude'])+str(k['Longitude'])))
                        yield k
                    else:
                        topop += 1
        result_coords = list(zip(result_lats,result_longs))
        logzilla.info(f'Zipcodes remaining: {search.zipcodes_remaining()}; Last request yields {len(result_coords)-topop} stores.')
        search.update_with(result_coords)
        coord = search.next()
    logzilla.info(f'Finished grabbing data!!')



def scrape():
    url="https://www.sierra.com/"
    field_defs = SimpleScraperPipeline.field_definitions(
        locator_domain = ConstantField(url),
        page_url=MappingField(mapping=['page_url']),
        location_name=MappingField(mapping=['Name']),
        latitude=MappingField(mapping=['Latitude']),
        longitude=MappingField(mapping=['Longitude']),
        street_address=MultiMappingField(mapping=[['Address'],['Address2']], multi_mapping_concat_with = ', ', value_transform = lambda x : x.replace(   'None','')),
        city=MappingField(mapping=['City'], value_transform = lambda x : x.replace('None','<MISSING>')),
        state=MappingField(mapping=['State'], value_transform = lambda x : x.replace('None','<MISSING>')),
        zipcode=MappingField(mapping=['Zip'], value_transform = lambda x : x.replace('None','<MISSING>'), is_required = False),
        country_code=MappingField(mapping=['Country'], value_transform = lambda x : x.replace('None','<MISSING>')),
        phone=MappingField(mapping=['Phone'], value_transform = lambda x : x.replace('None','<MISSING>') , is_required = False),
        store_number=MappingField(mapping=['StoreID']),
        hours_of_operation=MappingField(mapping=['Hours']),
        location_type=MissingField()
    )

    pipeline = SimpleScraperPipeline(scraper_name='sierra.com',
                                     data_fetcher=fetch_data,
                                     field_definitions=field_defs,
                                     log_stats_interval=15)

    pipeline.run()

if __name__ == "__main__":
    scrape()
