from sgscrape.simple_scraper_pipeline import *
from sgscrape import simple_network_utils as net_utils
from sgscrape import simple_utils as utils
import json


def para(tup):
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'}
    k = {}
    try:
        k = next(net_utils.fetch_xml(root_node_name='body',
                                location_node_name='script',
                                location_node_properties={'type':'application/ld+json','class':False},
                                request_url=tup[1],
                                headers=headers))
        k = json.loads(str(k['script type=application/ld+json']).rsplit(';',1)[0])
    except:
        #'name'
        #'@type'
        #'openingHours'
        z = next(net_utils.fetch_xml(root_node_name='body',
                                     location_node_name='div',
                                     location_node_properties={'class':'col12 stoney'},
                                     request_url=tup[1],
                                     headers=headers))
        k['openingHours'] = z['div class=[col3b]']['div class=[sidebar]']['div class=[info]']['div class=[loc_hours_holder]']['div class=[loc_hours_holder]'].replace('Hours:','').replace('  ','').replace('\n','; ')
        k['name'] = z['div class=[col9]']['h1']['h1']
        k['@type'] = "<MISSING>"
    
    k['index'] = tup[0]
    k['requrl'] = tup[1]
    yield k

    
def fetch_data():
    url = 'https://handandstone.ca/wp-admin/admin-ajax.php?action=store_search&lat=0&lng=0&inLoad=false&max_results=20000&radius=100000'
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'}
    son = net_utils.fetch_json(request_url = url,headers = headers)
    grabit = utils.parallelize(
                search_space = [[counter,i['url']] for counter, i in enumerate(son[0])],
                fetch_results_for_rec = para,
                max_threads = 10,
                print_stats_interval = 10
                )
    for i in grabit:
        for h in i:
            h['dic'] = son[0][h['index']]
            if 'OPEN' in h['dic']['phone']:
                h['dic']['phone'] = '<MISSING>'
                h['@type'] = 'Coming Soon'
            yield h
            
  
def scrape():
    url="https://handandstone.ca/"
    field_defs = SimpleScraperPipeline.field_definitions(
        locator_domain=ConstantField(url),
        page_url=MappingField(mapping=['dic','url']),
        location_name=MappingField(mapping=['name']),
        latitude=MappingField(mapping=['dic','lat']),
        longitude=MappingField(mapping=['dic','lng']),
        street_address=MultiMappingField(mapping=[['dic','address'],['dic','address2']], multi_mapping_concat_with = ', '),
        city=MappingField(mapping=['dic','city']),
        state=MappingField(mapping=['dic','state']),
        zipcode=MappingField(mapping=['dic','zip']),
        country_code=MappingField(mapping=['dic','country']),
        phone=MappingField(mapping=['dic','phone']),
        store_number=MappingField(mapping=['dic','id']),
        hours_of_operation=MappingField(mapping=['openingHours']),
        location_type=MappingField(mapping=['@type'], is_required = False)
    )

    pipeline = SimpleScraperPipeline(scraper_name='handandstone.ca',
                                     data_fetcher=fetch_data,
                                     field_definitions=field_defs,
                                     log_stats_interval=5)

    pipeline.run()

if __name__ == "__main__":
    scrape()
