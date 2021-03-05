from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.simple_scraper_pipeline import *
from sgscrape import simple_network_utils as net_utils
import json

session = SgRequests()
                  
def fetch_data():
    data={}
    url="https://roadys.com/roadys-truck-stops/"
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
           }
    r = net_utils.fetch_xml(
                        root_node_name='body',
                        location_node_name='ul',
                        location_node_properties={'class':'locationslist congtainer'},
                        request_url=url,
                        headers=headers
                        )
    for i in r:
        for j in i.keys():
            data['main']=j
            data['sec']=i[j]['div class=[locationcard]']
            data['url']=data['sec']['div class=[amenityactions]']
            h=[]
            for k in data['url'].items():
                h.append(k)
                
            data['url']="https://roadys.com"+h[1][0].split('href=')[1].split('style=')[0].rstrip()
            data['id']=data['url'].split('location/')[1].split('/')[0]
            header = {
                    'Accept' : '*/*',
                    'accept-encoding' : 'gzip, deflate, br',
                    'accept-language' : 'en-US,en;q=0.9,ro;q=0.8',
                    'content-length' : '8',    
                    'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
                    #'cookie': '_ga=GA1.2.1507372436.1604403080; _gid=GA1.2.578327646.1604403080; tk_or=%22%22; tk_r3d=%22%22; tk_lr=%22%22; PHPSESSID=d2c2764d37ad9cd186f977575637d3f8; chatlio_uuid--dd4bea79-cf5e-47e8-6fe3-056283136d78=88d72346-dfa4-48c7-a7b4-8a5812888c1c; ci_id=35cc8b43-d0b6-4e91-a383v2-t1758ddf044a-2466ca021e35; chatlio_rt--dd4bea79-cf5e-47e8-6fe3-056283136d78=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjZVVVSUQiOiJkZDRiZWE3OS1jZjVlLTQ3ZTgtNmZlMy0wNTYyODMxMzZkNzgiLCJleHAiOjE2Njc0ODIzNjMsImlhdCI6MTYwNDQxMDM2MywidnNVVUlEIjoiODhkNzIzNDYtZGZhNC00OGM3LWE3YjQtOGE1ODEyODg4YzFjIn0.Nl3lTor-GQUJ70N-SP-IcZfd0YwAr3k6umtsKoFsSmo; chatlio_at--dd4bea79-cf5e-47e8-6fe3-056283136d78=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjZVVVSUQiOiJkZDRiZWE3OS1jZjVlLTQ3ZTgtNmZlMy0wNTYyODMxMzZkNzgiLCJleHAiOjE2MDQ0MTc1NjMsImlhdCI6MTYwNDQxMDM2MywidnNVVUlEIjoiODhkNzIzNDYtZGZhNC00OGM3LWE3YjQtOGE1ODEyODg4YzFjIn0.gxOwPjIVJQ6OChVNEjx_GeSAkGiraIWGtrOnOJ_1TwQ; _gat=1 ',
                    'origin': 'https://roadys.com',
                    'referer': data['url'],
                    'sec-fetch-dest': '',
                    'sec-fetch-mode': 'cors',
                    'sec-fetch-site': 'same-origin',
                    'user-agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36',
                    'x-requested-with': 'XMLHttpRequest',
            }
            r2 = session.post(
                url="https://roadys.com/wp-content/plugins/roadys-locations/getSingleLocation.php",
                headers = header,
                data={'lid':data['id']})
            soup = BeautifulSoup(r2.text, 'lxml')
            data['subpage']=soup.find('div',class_='rloc_address')
            yield data

def scrape():
    url="https://roadys.com/"
    field_defs = SimpleScraperPipeline.field_definitions(
        locator_domain=ConstantField(url),
        page_url=MappingField(mapping=['url']),
        location_name=MappingField(mapping=['sec','div class=[locationheading]'],value_transform = lambda x : x.split("'span': {'span'")[1].split('}')[0].split('"')[1].lstrip().rstrip()),
        latitude=MappingField(mapping=['sec','div class=[locationheading]','div class=[headingleft]'], value_transform = lambda x : x.split('newLocation(')[1].split(',')[0]),
        longitude=MappingField(mapping=['sec','div class=[locationheading]','div class=[headingleft]'], value_transform = lambda x : x.split('newLocation(')[1].split(',')[1]),
        street_address=MappingField(mapping=['subpage'], value_transform = lambda x : x.split('<br/>')[0].split('address">')[1]),
        city=MappingField(mapping=['main'], value_transform = lambda x : x.split('city=')[1].split(' loc')[0]),
        state=MappingField(mapping=['main'], raw_value_transform = lambda x :  x.split('state=')[1].split(' cit')[0]),
        zipcode=MappingField(mapping=['main'], raw_value_transform = lambda x :  x.split('postalcode=')[1].split(' loc')[0]),
        country_code=ConstantField("US"),
        phone=MappingField(mapping=['sec','div class=[locationheading]','div class=[headingleft]','div class=[addressblock]','div class=[rblock]','div class=[phone]'], value_transform = lambda x : x if x!='{}' else "<MISSING>"),
        store_number=MappingField(mapping=['sec','div class=[locationheading]','div class=[headingleft]'], value_transform = lambda x : x.split('newLocation(')[1].split(',')[2]),
        hours_of_operation=ConstantField("<MISSING>"),#currently all stores are 24/7 from what I've noticed. I would need to make a request per store to just grab the '24/7' data
        location_type=MappingField(['main'], raw_value_transform = lambda x :  x.split('locationtype=')[1].split(' cla')[0])
    )

    pipeline = SimpleScraperPipeline(scraper_name='roadys.com',
                                     data_fetcher=fetch_data,
                                     field_definitions=field_defs,
                                     log_stats_interval=5,
                                     post_process_filter=lambda rec: rec.location_type() != 'Coming Soon!')

    pipeline.run()

if __name__ == "__main__":
    scrape()
