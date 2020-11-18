from sgscrape.simple_scraper_pipeline import *
from sgscrape import simple_network_utils as net_utils
from sgscrape import simple_utils as utils
import json



    
def fetch_data():
    url = "https://handandstone.com/api/v1/locations?distance=0&page=1&per-page=100&sort=distance"
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'}
    cont = True
    while cont:
        son = net_utils.fetch_json(request_url = url,headers = headers)
        for i in son[0]['locations']:
            try:
                i['worktime'] = pretty_hours(i['worktime'])
            except:
                i['worktime'] = "<MISSING>"
            yield i
        try:
            url = son[0]['links']['next']['href']
        except:
            cont = False
def pretty_hours(x):
    hours = []
    for i in x:
        hours.append(str(i['day']+': '+str(i['opened'])+'-'+str(i['closed'])))
    return '; '.join(hours)
def scrape():
    url="https://handandstone.com/"
    field_defs = SimpleScraperPipeline.field_definitions(
        locator_domain=ConstantField(url),
        page_url=MappingField(mapping=['slug'], value_transform = lambda x : "https://handandstone.com/locations/"+x),
        location_name=MappingField(mapping=['name']),
        latitude=MappingField(mapping=['latitude']),
        longitude=MappingField(mapping=['longitude']),
        street_address=MappingField(mapping=['address']),
        city=MappingField(mapping=['city']),
        state=MappingField(mapping=['state']),
        zipcode=MappingField(mapping=['zip']),
        country_code=MappingField(mapping=['timezone_name'], value_transform = lambda x : "US" if 'America' in x else "<MISISNG>"),
        phone=MultiMappingField(mapping=[['area'],['phone']], multi_mapping_concat_with = ' ', is_required = False),
        store_number=MappingField(mapping=['id']),
        hours_of_operation=MappingField(mapping=['worktime']),
        location_type=MappingField(mapping=['is_coming_soon'], value_transform = lambda x : "Coming Soon" if x == True else "<MISSING>")
    )

    pipeline = SimpleScraperPipeline(scraper_name='handandstone.com',
                                     data_fetcher=fetch_data,
                                     field_definitions=field_defs,
                                     log_stats_interval=5)

    pipeline.run()

if __name__ == "__main__":
    scrape()
