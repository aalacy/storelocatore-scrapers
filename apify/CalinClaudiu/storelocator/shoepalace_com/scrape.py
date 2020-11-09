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
        if i['id'] == 16973819:
            i['parsed']['StateName'] = 'FL'
            i['parsed']['PlaceName'] = 'Miami'
            i['parsed']['OccupancyType'] = ''
            #fixing odd case with usaddress
        if i['id'] == 16973848:
            i['parsed']['AddressNumberPrefix'] = 'GLENDALE GALLERIA'
        if i['id'] == 16973741:
            i['parsed']['AddressNumberPrefix'] = '500 LAKEWOOD CENTER MALL SPACE '
            
        yield i

def scrape():
    url="https://www.shoepalace.com/"
    field_defs = SimpleScraperPipeline.field_definitions(
        locator_domain=ConstantField(url),
        page_url=MappingField(mapping=['url'], is_required = False),
        location_name=MappingField(mapping=['name']),
        latitude=MappingField(mapping=['latitude']),
        longitude=MappingField(mapping=['longitude']),
        street_address=MultiMappingField(mapping=[['parsed','AddressNumberPrefix'],['parsed','AddressNumber'],['parsed','AddressNumberSuffix'],['parsed','StreetNamePreDirectional'],['parsed','StreetNamePreModifier'],['parsed','StreetNamePreType'],['parsed','StreetName'],['parsed','StreetNamePostDirectional'],['parsed','StreetNamePostModifier'],['parsed','StreetNamePostType'],['parsed','OccupancyType'],['parsed','OccupancyIdentifier'],['parsed','SubaddressType'],['parsed','SubaddressIdentifier']], multi_mapping_concat_with=' ', part_of_record_identity = True),
        city=MappingField(mapping=['parsed','PlaceName'], is_required = False),
        state=MappingField(mapping=['parsed','StateName'], is_required = False),
        zipcode=MappingField(mapping=['parsed','ZipCode'], is_required = False),
        country_code=ConstantField("US"),
        phone=MappingField(mapping=['phone']),
        store_number=MappingField(mapping=['id']),
        hours_of_operation=MultiMappingField(mapping=[['custom_field_1'], ['custom_field_2'], ['custom_field_3']], multi_mapping_concat_with=', '),
        location_type=MappingField(mapping=['category'])
    )

    pipeline = SimpleScraperPipeline(scraper_name='roadys.com',
                                     data_fetcher=fetch_data,
                                     field_definitions=field_defs,
                                     log_stats_interval=5)

    pipeline.run()

if __name__ == "__main__":
    scrape()
