from sgscrape.simple_scraper_pipeline import *
from sgscrape import simple_network_utils as net_utils
from sgscrape import simple_utils as utils
import json
from sgzip import DynamicGeoSearch, SearchableCountries
from sglogging import sglog

log = sglog.SgLogSetup().get_logger(logger_name='petsuppliesplus.com')
def para(tup):
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'}
    k = json.loads(str(next(net_utils.fetch_xml(root_node_name='body',
                                location_node_name='script',
                                location_node_properties={'type':'application/ld+json'},
                                request_url=tup[1],
                                headers=headers))['script type=application/ld+json']).rsplit(';',1)[0])
    k['index'] = tup[0]
    k['requrl'] = tup[1]
    yield k
    
def fetch_data():
    
    url = "https://petsuppliesplus.com"
    testur = "https://petsuppliesplus.com/api/sitecore/Store/Search?searchQuery=&pageSize=0&fromRowNumber=0"
    headerz = {
    'Host': 'petsuppliesplus.com',
    'Connection': 'keep-alive',
    'Cache-Control': 'max-age=0',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-User': '?1',
    'Sec-Fetch-Dest': 'document',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-US,en;q=0.9,ro;q=0.8',
    'Cookie': ''}
    
    search = DynamicGeoSearch(country_codes=[SearchableCountries.USA])
    search.initialize()
    coord = search.next()
    while coord:
        lat, long = coord
        headerz['Cookie'] = str(''.join(['SearchCityLat=',str(lat),';','SearchCityLng=',str(long),';']))
        son = net_utils.fetch_json(request_url = testur, headers = headerz)
        result_lats = []
        result_longs = []
        result_coords = []
        j = utils.parallelize(
            search_space = [[counter,url+i['StorePageUrl']] for counter, i in enumerate(son[0]['NearbyStores'])],
            fetch_results_for_rec = para,
            max_threads = 10,
            print_stats_interval = 10
            )
        for i in j:
            for p in i:
                kk = p['index']
                son[0]['NearbyStores'][kk]['data'] = p
                son[0]['NearbyStores'][kk]['hourz'] = []
                result_lats.append(son[0]['NearbyStores'][kk]['LatPos'])
                result_longs.append(son[0]['NearbyStores'][kk]['LngPos'])
                for day in son[0]['NearbyStores'][kk]['data']['openingHoursSpecification']:
                    son[0]['NearbyStores'][kk]['hourz'].append(str(day['dayOfWeek'][0]+'  '+day['opens']+'-'+day['closes']))
                son[0]['NearbyStores'][kk]['hourz'] = ', '.join(son[0]['NearbyStores'][kk]['hourz'])
                yield son[0]['NearbyStores'][kk]
        result_coords = list(zip(result_lats,result_longs))
        
        log.info(f'Coordinates remaining: {search.zipcodes_remaining()}; Last request yields {len(result_coords)} stores.')
        search.update_with(result_coords)
        coord = search.next()
    log.info(f'Finished grabbing data!!')



def scrape():
    url="https://petsuppliesplus.com/"
    field_defs = SimpleScraperPipeline.field_definitions(
        locator_domain = ConstantField(url),
        page_url=MappingField(mapping=['data','requrl']),
        location_name=MappingField(mapping=['FormattedStoreName']),
        latitude=MappingField(mapping=['LatPos']),
        longitude=MappingField(mapping=['LngPos']),
        street_address=MappingField(mapping=['data','address','streetAddress']),
        city=MappingField(mapping=['City']),
        state=MappingField(mapping=['StateCode']),
        zipcode=MappingField(mapping=['Zip']),
        country_code=MappingField(mapping=['data','address','addressCountry']),
        phone=MappingField(mapping=['Phone'], part_of_record_identity = True),
        store_number=MappingField(mapping=['StoreId'], part_of_record_identity = True),
        hours_of_operation=MappingField(mapping=['hourz']),
        location_type=MissingField()
    )

    pipeline = SimpleScraperPipeline(scraper_name='petsuppliesplus.com',
                                     data_fetcher=fetch_data,
                                     field_definitions=field_defs,
                                     log_stats_interval=15)

    pipeline.run()

if __name__ == "__main__":
    scrape()
