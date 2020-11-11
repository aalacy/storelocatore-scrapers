from sgscrape.simple_scraper_pipeline import *
from sgscrape import simple_network_utils as net_utils
from sgscrape import simple_utils as utils
import json
from sglogging import sglog
from sgselenium import SgFirefox, SgSelenium
import re
import time

def para(tup):
    k = {}
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'}
    if len(tup[1])>0:
        k = json.loads(next(net_utils.fetch_xml(root_node_name='body',
                                location_node_name='script',
                                location_node_properties={'type':'application/ld+json', 'id':'schema-webpage'},
                                request_url=tup[1],
                                headers=headers))['script type=application/ld+json id=schema-webpage'], strict=False)#['script type=application/ld+json']).rsplit(';',1)[0])
    else:
        k['requrl'] = "<MISSING>"        
        k['index'] = tup[0]
    
    k['index'] = tup[0]
    k['requrl'] = tup[1]
    yield k


def fetch_data():
    brands = ['pii', #0-Park Inn
              'rdb', #1-Radisson Blu
              'rdr', #2-Radisson RED
              'art', #3-art'otel
              'rad', #4-Radisson Hotel
              'ri',  #5-Radisson Individuals
              'prz', #6-??? Empty
              'pph', #7-Park Plaza
              'cis', #8-Country Inn & Suites by Radisson ###DONE
              'rco'  #9-Radisson Collection Paradise Resort
              ]
    url = "https://www.radissonhotels.com/en-us/destination"
    brand = brands[8]
    logzilla = sglog.SgLogSetup().get_logger(logger_name=brand)
    logzilla.info(f'Selected brand: {brand}')
    #Brand selector
    son = []
    with SgFirefox() as driver:
        driver.get("https://www.radissonhotels.com/en-us/destination")
        time.sleep(10)
        for r in driver.requests:
            if r.path=="/zimba-api/destinations/hotels":
                son.append(r.response.body)
    for i in son:
        i = i.decode()
        k = json.loads(i)
        if len(k['hotels'])!= 0:
            if k['hotels'][0]['brand'] == brand:
                print(k['hotels'][0]['overviewPath'])
                par = utils.parallelize(
                    search_space = [[counter,z['overviewPath']] for counter, z in enumerate(k['hotels'])],
                    fetch_results_for_rec = para,
                    max_threads = 10,
                    print_stats_interval = 10
                                        )
                for a in par:
                    for store in a:
                        yield {'main':k['hotels'][store['index']], 'sub':store}
    logzilla.info(f'Finished grabbing data!!')
def validatorsux(x):
    if x=='Wisconsin':
        x="WI"
    if x=='Washington':
        x="WA"
    if x=='West Virginia':
        x="WV"
    if x=='Wyoming':
        x="WY"
    return x

def scrape():
    url="https://countryinns.com"
    field_defs = SimpleScraperPipeline.field_definitions(
        locator_domain = ConstantField(url),
        page_url=MappingField(mapping=['sub','requrl']),
        location_name=MappingField(mapping=['main','name']),
        latitude=MappingField(mapping=['main','coordinates','latitude']),
        longitude=MappingField(mapping=['main','coordinates','longitude']),
        street_address=MappingField(mapping=['sub','mainEntity','address','streetAddress']),
        city=MappingField(mapping=['sub','mainEntity','address','addressLocality']),
        state=MappingField(mapping=['sub','mainEntity','address','addressRegion'], value_transform = validatorsux, is_required = False),
        zipcode=MappingField(mapping=['sub','mainEntity','address','postalCode']),
        country_code=MappingField(mapping=['sub','mainEntity','address','addressCountry']),
        phone=MappingField(mapping=['sub','mainEntity','telephone',0]),
        store_number=MappingField(mapping=['main','code']),
        hours_of_operation=MissingField(),
        location_type=MappingField(mapping=['sub','mainEntity','@type'])
    )

    pipeline = SimpleScraperPipeline(scraper_name='countryinns.com',
                                     data_fetcher=fetch_data,
                                     field_definitions=field_defs,
                                     log_stats_interval=15)

    pipeline.run()

if __name__ == "__main__":
    scrape()
