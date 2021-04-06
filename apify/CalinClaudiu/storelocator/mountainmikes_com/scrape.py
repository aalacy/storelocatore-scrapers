from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.simple_scraper_pipeline import *
from sgscrape import simple_network_utils as net_utils
import json

session = SgRequests()
                                       
def fetch_data():
    stores={}
    
    url="https://www.mountainmikespizza.com/locations/"
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
           }
    
    r = session.get(url, headers=headers)
    soup = BeautifulSoup(r.text, 'lxml')
    states = soup.find_all('div', class_="state_block")
    for state in states:       
        atag = state.find_all('div', class_=lambda value: value and value.startswith("location_block store"))
        for tag in atag:
            if tag.has_attr('data-lat'):
                if not tag.find('div', class_="store_status") or tag.find('div', class_="store_status").get_text()!='Coming Soon!':
                    #if it is not coming soon
                    now=tag.find('a', class_="cta link_style cta_angle_rt cta_hover pine_bkd")['href']
                    r2=net_utils.fetch_xml(
                        root_node_name='main',
                        location_node_name='script',
                        location_node_properties={'type':'application/ld+json','class':False},
                        request_url=now,
                        headers=headers
                        )
                    
                    for j in r2:
                        son = json.loads(j['script type=application/ld+json'])
                    data={}
                    data['tag']=tag
                    data['json']=son
                    data['page_url']=now
                    yield data


def scrape():
    field_defs = SimpleScraperPipeline.field_definitions(
        locator_domain= MappingField(mapping=['json','url']),
        page_url=MappingField(mapping=['page_url']),
        location_name=MappingField(mapping=['tag'],raw_value_transform = lambda x : x.find('a', class_="cta link_style cta_angle_rt cta_hover pine_bkd").get_text().split("for")[1].lstrip().rstrip()),
        latitude=MappingField(mapping=['tag','data-lat']),
        longitude=MappingField(mapping=['tag','data-long']),
        street_address=MappingField(mapping=['json','address','streetAddress'], raw_value_transform = lambda x : x.split(',')[0]),
        city=MappingField(['json','address','addressLocality']),
        state=MappingField(['json','address','addressRegion']),
        zipcode=MappingField(['json','address','postalCode']),
        country_code=MappingField(['json','address','addressCountry']),
        phone=MappingField(['json','telephone'], is_required = False),
        store_number=MappingField(['tag','class'], raw_value_transform = lambda x : x[1].rsplit('_')[1]),
        hours_of_operation=MappingField(['json','openingHours'], raw_value_transform = lambda x : x[0].replace('[','').replace(']','').replace("'",'')),
        location_type=MappingField(['json','@type'])
    )

    pipeline = SimpleScraperPipeline(scraper_name='mountainmikespizza.com',
                                     data_fetcher=fetch_data,
                                     field_definitions=field_defs,
                                     log_stats_interval=5,
                                     post_process_filter=lambda rec: rec.location_type() != 'Coming Soon!')

    pipeline.run()

if __name__ == "__main__":
    scrape()

