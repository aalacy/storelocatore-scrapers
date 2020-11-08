from sgscrape.simple_scraper_pipeline import *
from sgscrape import simple_network_utils as net_utils
from sgscrape import simple_utils as utils
import json

def fetch_data():
    url = "https://modpizza.com/wp-admin/admin-ajax.php?action=bh_storelocator_posts_query_ajax&postType=bh_sl_locations&security=52fc35ca62"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36'}
     
    j = net_utils.fetch_json(request_url = url,
               headers = headers)

    for i in j[0]:
        son = json.dumps(i)
        son = json.loads(son)
        yield son

def pretty_phone(x):
    x = x.encode('utf-8')
    try:
        x = repr(x).replace('\\u00a','')
    except:
        x = x
    try:
        x = repr(x).replace("b'",'')
    except:
        x = x
    try:
        x = repr(x).replace("xc2",'')
    except:
        x = x
    try:
        x = repr(x).replace("xa0",'')
    except:
        x = x
    try:
        x = repr(x).replace("xe2",'')
    except:
        x = x
    try:
        x = repr(x).replace("x80",'')
    except:
        x = x
    try:
        x = repr(x).replace("xad",'')
    except:
        x = x
    try:
        x = repr(x).replace("xac",'')
    except:
        x = x
    try:
        x = repr(x).replace("\\",'')
    except:
        x = x
    try:
        x = repr(x).replace("'",'')
    except:
        x = x
    return x.replace("\\", "").replace('"','').replace("'",'')

def scrape():
    url="https://modpizza.com/"
    field_defs = SimpleScraperPipeline.field_definitions(
        locator_domain = ConstantField(url),
        page_url=MappingField(mapping=['permalink']),
        location_name=MappingField(mapping=['name'], value_transform = lambda x : x.replace('&#8211;','')),
        latitude=MappingField(mapping=['lat']),
        longitude=MappingField(mapping=['lng']),
        street_address=MultiMappingField(mapping=[['address'],['address2']], multi_mapping_concat_with = ', '),
        city=MappingField(mapping=['city']),
        state=MappingField(mapping=['state']),
        zipcode=MappingField(mapping=['postal'], value_transform = lambda x : x if x!='482424' else '48242'),
        country_code=MappingField(mapping=['country'], value_transform = lambda x : "US" if x=='' else x),
        phone=MappingField(mapping=['phone'], value_transform = pretty_phone, is_required = False ),
        store_number=MappingField(mapping=['store_id'], is_required = False),
        hours_of_operation=MultiMappingField(mapping=[['hours1'],['hours2'],['hours3'],['hours4'],['hours5'],['hours6'],['hours7']], multi_mapping_concat_with = ', ', is_required = False),
        location_type=MappingField(mapping=['bh_sl_loc_cat'], value_transform = lambda x : x if not '-' in x else x.split(' - ')[1])
    )

    pipeline = SimpleScraperPipeline(scraper_name='modpizza.com',
                                     data_fetcher=fetch_data,
                                     field_definitions=field_defs,
                                     log_stats_interval=15)

    pipeline.run()

if __name__ == "__main__":
    scrape()
