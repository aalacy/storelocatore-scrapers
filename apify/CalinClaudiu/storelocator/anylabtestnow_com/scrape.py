from sgscrape.simple_scraper_pipeline import *
from sgscrape import simple_network_utils as net_utils
import json
import re

def fetch_data():
    data={}
    url="https://www.anylabtestnow.com/locations/"
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
           }

    r = net_utils.fetch_xml(
        root_node_name='body',
        location_node_name='section',
        location_node_properties={'id':'content'},
        request_url=url,
        headers=headers)
    for j in r:
        k=j['script type=text/javascript']['script type=text/javascript']
    k = k.split("JSON.parse('")[1]
    k = k.split("]');")[0]
    k = k.split('[',1)[1]
    k = '{"stores":['+k+']}'
    son = json.loads(k)
    for i in son['stores']:
        yield i
        
def parsephn(bad):
    good = re.compile('[^0-9]')
    bad = good.sub('',bad)
    good = bad
    return good
    
def scrape():
    url="https://www.anylabtestnow.com/"
    field_defs = SimpleScraperPipeline.field_definitions(
        locator_domain=ConstantField(url),
        page_url=MappingField(mapping=['url']),
        location_name=MappingField(mapping=['title']),
        latitude=MappingField(mapping=['latitude']),
        longitude=MappingField(mapping=['longitude']),
        street_address=MappingField(mapping=['address']),
        city=MappingField(mapping=['city']),
        state=MappingField(mapping=['state']),
        zipcode=MappingField(mapping=['zip']),
        country_code=ConstantField("US"),
        phone=MappingField(mapping=['phone'], value_transform = parsephn),
        store_number=MappingField(mapping=['id']),
        hours_of_operation=MappingField(mapping=['hours'], value_transform = lambda x : x.replace("{'day': '",'').replace("', 'start': '",' ').replace("', 'end': '",'-').replace("'}",'').replace('[','').replace(']','')),
        location_type=MappingField(mapping=['services'], value_transform= lambda x : x.replace('[','').replace(']','').replace("'",''), is_required = False)
    )

    pipeline = SimpleScraperPipeline(scraper_name='anylabtestnow.com',
                                     data_fetcher=fetch_data,
                                     field_definitions=field_defs,
                                     log_stats_interval=5)

    pipeline.run()

if __name__ == "__main__":
    scrape()
