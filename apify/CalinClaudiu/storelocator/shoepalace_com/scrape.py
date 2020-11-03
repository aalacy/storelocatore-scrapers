from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.simple_scraper_pipeline import *
from sgscrape import simple_network_utils as net_utils
import usaddress
import json
session = SgRequests()
                  
def fetch_data():
    data={}
    url="https://storemapper-herokuapp-com.global.ssl.fastly.net/api/users/8158/stores.js?callback=SMcallback2"
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
           }
    query_params = {"callback": "SMcallback2"}

    r = net_utils.fetch_html(request_url=url,query_params=query_params,headers=headers)

    for j in r:
        k=j['p']['p']
        
    k = k.split("SMcallback2(")[1]
    k = k.split('{',1)[1]
    k = k.replace(']})',']')
    k = '{'+k+'}'
    son = json.loads(k)
    for i in son['stores']:
        i['parsed'] = dict(usaddress.parse(i['address']))
        i['parsed'] = {value : key for (key, value) in i['parsed'].items()}
        yield i

def scrape():
    url="https://www.shoepalace.com/"
    field_defs = SimpleScraperPipeline.field_definitions(
        locator_domain=ConstantField(url),
        page_url=MappingField(mapping=['url'], is_required = False),
        location_name=MappingField(mapping=['name']),
        latitude=MappingField(mapping=['latitude']),
        longitude=MappingField(mapping=['longitude']),
        street_address=MultiMappingField(mapping=[['parsed','AddressNumberPrefix'],['parsed','AddressNumber'],['parsed','AddressNumberSuffix'],['parsed','StreetNamePreDirectional'],['parsed','StreetNamePreModifier'],['parsed','StreetNamePreType'],['parsed','StreetName'],['parsed','StreetNamePostDirectional'],['parsed','StreetNamePostModifier'],['parsed','StreetNamePostType'],['parsed','OccupancyType'],['parsed','OccupancyIdentifier']], multi_mapping_concat_with=' '),
        city=MappingField(mapping=['parsed','PlaceName']),
        state=MappingField(mapping=['parsed','StateName']),
        zipcode=MappingField(mapping=['parsed','ZipCode'],is_required = False),
        country_code=ConstantField("US"),
        phone=MappingField(mapping=['phone']),
        store_number=MappingField(mapping=['id']),
        hours_of_operation=MultiMappingField(mapping=[['custom_field_1'], ['custom_field_2'], ['custom_field_3']], multi_mapping_concat_with=', '),#currently all stores are 24/7 from what I've noticed. I would need to make a request per store to just grab the '24/7' data
        location_type=MappingField(mapping=['category'])
    )

    pipeline = SimpleScraperPipeline(scraper_name='roadys.com',
                                     data_fetcher=fetch_data,
                                     field_definitions=field_defs,
                                     log_stats_interval=5)

    pipeline.run()

if __name__ == "__main__":
    scrape()
