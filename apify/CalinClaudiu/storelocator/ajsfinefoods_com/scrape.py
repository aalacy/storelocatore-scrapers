from sgscrape.simple_scraper_pipeline import *
from sgscrape import simple_network_utils as net_utils
from sgscrape import simple_utils as utils
from sgrequests import SgRequests
from sglogging import sglog
from sgzip import DynamicGeoSearch, SearchableCountries
import sgzip
from bs4 import BeautifulSoup as b4
import json

def fetch_data():
    logzilla = sglog.SgLogSetup().get_logger(logger_name='Scraper')
    url = "https://www.ajsfinefoods.com/wp-admin/admin-ajax.php?action=store_search&lat="
    url2="&max_results=100&search_radius=500"
    #33.5114334&lng=-112.0685027
    headers = {
                'User-Agent' : 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36'        }
    session = SgRequests()

    hours = session.get('https://www.ajsfinefoods.com/locations/',headers = headers)
    soup = b4(hours.text, 'lxml')

    hours = soup.find_all('p')
    horas = ''
    for i in hours:
        if 'Hours of Operation' in i.text:
            horas = i.text.split('peration:')[1].strip()


    
    search = sgzip.DynamicGeoSearch(country_codes=[SearchableCountries.USA], max_radius_miles=500, max_search_results=100)

    search.initialize()

    coord = search.next()
    identities = set()
    while coord:
        lat, long = coord # extract lat/long from the coord tuple
        son = session.get(url+str(lat)+'&lng='+str(long)+url2, headers = headers).json()
        result_lats = []
        result_longs = []
        result_coords = []
        topop = 0
        if len(son)!=0:
                for k in son:
                    k['hours'] = horas
                    result_lats.append(k['lat'])
                    result_longs.append(k['lng'])
                    if str(str(k['lat'])+str(k['lng'])) not in identities:
                        identities.add(str(str(k['lat'])+str(k['lng'])))
                        yield k
                    else:
                        topop += 1
        result_coords = list(zip(result_lats,result_longs))
        logzilla.info(f'Coords remaining: {search.zipcodes_remaining()}; Last request yields {len(result_coords)-topop} stores.')
        search.update_with(result_coords)
        coord = search.next()

    

        
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
    url="https://www.ajsfinefoods.com/"
    field_defs = SimpleScraperPipeline.field_definitions(
        locator_domain = ConstantField(url),
        page_url=MappingField(mapping=['url'], is_required = False),
        location_name=MappingField(mapping=['store'], value_transform = lambda x : x.replace('None','<MISSING>')),
        latitude=MappingField(mapping=['lat']),
        longitude=MappingField(mapping=['lng']),
        street_address=MultiMappingField(mapping=[['address'],['address2']], multi_mapping_concat_with = ', ', value_transform = fix_comma),
        city=MappingField(mapping=['city'], value_transform = lambda x : x.replace('None','<MISSING>')),
        state=MappingField(mapping=['state'], value_transform = lambda x : x.replace('None','<MISSING>')),
        zipcode=MappingField(mapping=['zip'], value_transform = lambda x : x.replace('None','<MISSING>'), is_required = False),
        country_code=MappingField(mapping=['country']),
        phone=MappingField(mapping=['phone'], value_transform = lambda x : x.replace('None','<MISSING>') , is_required = False),
        store_number=MappingField(mapping=['id']),
        hours_of_operation=MappingField(mapping=['hours'], is_required = False),
        location_type=MissingField()
    )

    pipeline = SimpleScraperPipeline(scraper_name='ajsfinefoods.com',
                                     data_fetcher=fetch_data,
                                     field_definitions=field_defs,
                                     log_stats_interval=15)

    pipeline.run()

if __name__ == "__main__":
    scrape()
