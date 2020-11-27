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
    url = "https://www.loansbyworld.com/wp-admin/admin-ajax.php?action=store_search&lat="
    url2="&max_results=100&search_radius=100"
    #33.5114334&lng=-112.0685027
    headers = {'Host' : 'www.loansbyworld.com',
               'Connection':'keep-alive',
               'Accept': '*/*',
                'User-Agent' : 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36',
                 'X-Requested-With': 'XMLHttpRequest',
                'Sec-Fetch-Site': 'same-origin',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Dest': 'empty',
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept-Language': 'en-US,en;q=0.9,ro;q=0.8'
               }
    session = SgRequests()
    search = sgzip.DynamicGeoSearch(country_codes=[SearchableCountries.USA], max_radius_miles=100, max_search_results=100)

    search.initialize()

    coord = search.next()
    identities = set()
    while coord:
        lat, long = coord # extract lat/long from the coord tuple
        son = session.get(url+str(lat)+'&lng='+str(long)+url2, headers = headers).text
        ter = 0
        while '403 Forbidden' in son:
            ter += 1
            if ter > 500:
                raise Exception('Tried to grab this 500 times:\n\n{url+str(lat)+"&lng="+str(long)+url2}\n\nReason: 403 Forbidden\n\n No longer retrying :(')
                #it usually works after about 30 tries..
            logzilla.info(f'Can not grab following link:\n\n{url+str(lat)+"&lng="+str(long)+url2}\n\nReason: 403 Forbidden\n\nRetrying...')
            son = session.get(url+str(lat)+'&lng='+str(long)+url2, headers = headers).text
        if len(son)>5:
            try:
                son = son.replace('\n','')
                son = '['+son.split('[',1)[1]
            except:
                raise Exception('Failed getting this:\n\n{url+str(lat)+"&lng="+str(long)+url2}\n\nReason: odd json format\n\n ')
            try:
                son = json.loads(son)
            except:
                raise Exception('Failed getting this:\n\n{url+str(lat)+"&lng="+str(long)+url2}\n\nReason: odd json format\n\n ')
        else:
            son = ''
        result_lats = []
        result_longs = []
        result_coords = []
        topop = 0
        if len(son)!=0:
                for k in son:
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
def good_hours(k):
    h = []
    for i in list(k):
        h.append(str(i)+': '+str(k[i]['open'])+'-'+str(k[i]['close']))
    return '; '.join(h).replace('false-false','closed')
        
def scrape():
    url="https://www.loansbyworld.com/"
    field_defs = SimpleScraperPipeline.field_definitions(
        locator_domain = ConstantField(url),
        page_url=MappingField(mapping=['permalink'], is_required = False),
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
        hours_of_operation=MappingField(mapping=['uhours'], raw_value_transform = good_hours, is_required = False),
        location_type=MappingField(mapping=['branch_id'], value_transform = lambda x : 'BranchId: '+x)
    )

    pipeline = SimpleScraperPipeline(scraper_name='ajsfinefoods.com',
                                     data_fetcher=fetch_data,
                                     field_definitions=field_defs,
                                     log_stats_interval=15)

    pipeline.run()

if __name__ == "__main__":
    scrape()
