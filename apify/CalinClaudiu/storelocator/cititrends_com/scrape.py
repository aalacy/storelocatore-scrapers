from sgscrape.simple_scraper_pipeline import *
from sgscrape import simple_network_utils as net_utils
from sgscrape import simple_utils as utils
import bs4
from bs4 import BeautifulSoup
import json

def fetch_axml(request_url: str,
              root_node_name: str,
              location_node_name: str,
              method: str = 'GET',
              location_parser: Callable[[bs4.Tag], dict] = xml_to_dict,
              location_node_properties: Dict[str, str] = {},
              query_params: dict = {},
              data_params: dict = {},
              headers: dict = {},
              xml_parser: str = 'lxml',
              retries: int = 10) -> List[dict]:
    
    response = net_utils.fetch_data(request_url=request_url,
                          method=method,
                          data_params=data_params,
                          query_params=query_params,
                          headers=headers,
                          retries=retries)

    xml_result = BeautifulSoup(response.text, xml_parser)

    root_node = xml_result.find(root_node_name)

    location_nodes = root_node.find_all(location_node_name, location_node_properties)

    for location in location_nodes:
        yield {'dic' : location_parser(location),
               'xml' : xml_result,
               'requrl' :request_url}


def fetch_data():
    url = "https://locations.cititrends.com/"
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
           }
    states = net_utils.fetch_xml(
        root_node_name='body',
        location_node_name='li',
        location_node_properties={'class':'c-directory-list-content-item'},
        request_url=url,
        headers=headers)
    stores = {'state':[],'city':[],'store':[]}
    for j in states:
        link = list(j)[0].split('href=')[1]
        count = link.count('/')
        if count == 0:
            stores['state'].append(url+link)
        elif count == 1:
            stores['city'].append(url+link)
        else:
            stores['store'].append(url+link)
    #odd sitemap may show states, cities, or individual stores,
    #building states list
            
    for i in stores['state']:
        cities = net_utils.fetch_xml(
            root_node_name='body',
            location_node_name='li',
            location_node_properties={'class':'c-directory-list-content-item'},
            request_url=i,
            headers=headers)
        for j in cities:
            link = list(j)[0].split('href=')[1]
            count = link.count('/')
            if count == 1:
                stores['city'].append(url+link)
            else:
                stores['store'].append(url+link)
    #building city list

    for i in stores['city']:
        store = net_utils.fetch_xml(
            root_node_name='body',
            location_node_name='h2',
            location_node_properties={'class':'c-location-grid-item-title'},
            request_url=i,
            headers=headers)
        for j in store:
            link = i[0:-5]+'/'+list(j)[0].split('/')[-1].split(' title')[0]
            stores['store'].append(link)

    #building final store list

    
    j = utils.parallelize(
                search_space = stores['store'],
                fetch_results_for_rec = lambda x : fetch_axml(
                                                    root_node_name='body',
                                                    location_node_name='section',
                                                    location_node_properties={'id':'nap','class':'nap-section'},
                                                    request_url=x,
                                                    headers=headers),
                max_threads = 15,
                print_stats_interval = 15)
    for i in j:
        for h in i:
            h['xml'] = h['xml'].find('span', class_='location-name-geo').get_text()
            yield h


def pretty_hours(k):
    k = k.split('data-days=')[1]
    k = k.split(' data-showopentoday')[0]
    k = '{"hours":'+k+'}'
    k = json.loads(k)
    x = []
    for i in k['hours']:
        x.append(i['day']+' : '+str(i['intervals'][0]['start'])+'-'+str(i['intervals'][0]['end']))
    x = ', '.join(x)
    return x

def state_validator_pleasing(x):
    if x == 'Delaware':
        x = 'DE'
    if x == 'Wisconsin':
        x = 'WI'
    return x
    
 
         
def scrape():
    url="https://cititrends.com/"
    field_defs = SimpleScraperPipeline.field_definitions(
        locator_domain=ConstantField(url),
        page_url=MappingField(mapping=['requrl']),
        location_name=MappingField(mapping=['xml']),
        latitude=MappingField(mapping=['dic','div class=[nap]','div class=[row]','div class=[col-md-3, hidden-xs]','div class=[location-map-wrapper] id=schema-location itemprop=location itemscope= itemtype=http://schema.org/Place itemref=telephone address location-name','span class=[coordinates] itemprop=geo itemscope= itemtype=http://schema.org/GeoCoordinates'], value_transform = lambda x : x.split('itemprop=latitude content=')[1].split("'")[0]),
        longitude=MappingField(mapping=['dic','div class=[nap]','div class=[row]','div class=[col-md-3, hidden-xs]','div class=[location-map-wrapper] id=schema-location itemprop=location itemscope= itemtype=http://schema.org/Place itemref=telephone address location-name','span class=[coordinates] itemprop=geo itemscope= itemtype=http://schema.org/GeoCoordinates'], value_transform = lambda x : x.split('itemprop=longitude content=')[1].split("'")[0]),
        street_address=MultiMappingField(mapping=[['dic','div class=[nap]','div class=[row]','div class=[col-md-9]','div class=[row]','div class=[col-xs-12, col-sm-6, col-md-5, hidden-xs]','address class=[c-address]','span class=[c-address-street]','span class=[c-address-street-1]','span class=[c-address-street-1]'],
                                                  ['dic','div class=[nap]','div class=[row]','div class=[col-md-9]','div class=[row]','div class=[col-xs-12, col-sm-6, col-md-5, hidden-xs]','address class=[c-address]','span class=[c-address-street]','span class=[c-address-street-2]','span class=[c-address-street-2]']],
                                         multi_mapping_concat_with = ', ', is_required = False),
        #street_address=ConstantField(url),
        city=MappingField(mapping=['dic','div class=[nap]','div class=[row]','div class=[col-md-9]','div class=[row]','div class=[col-xs-12, col-sm-6, col-md-5, hidden-xs]','address class=[c-address]','span class=[c-address-city]','span','span']),
        state=MappingField(mapping=['dic','div class=[nap]','div class=[row]','div class=[col-md-9]','div class=[row]','div class=[col-xs-12, col-sm-6, col-md-5, hidden-xs]','address class=[c-address]','span class=[c-address-state]','span class=[c-address-state]'],
                           value_transform = state_validator_pleasing),
        zipcode=MappingField(mapping=['dic','div class=[nap]','div class=[row]','div class=[col-md-9]','div class=[row]','div class=[col-xs-12, col-sm-6, col-md-5, hidden-xs]','address class=[c-address]','span class=[c-address-postal-code]','span class=[c-address-postal-code]']),
        country_code=MappingField(mapping=['dic','div class=[nap]','div class=[row]','div class=[col-md-9]','div class=[row]','div class=[col-xs-12, col-sm-6, col-md-5, hidden-xs]','address class=[c-address]'], value_transform = lambda x : x.split(' c-address-country-')[-1].split("]': '")[-1].replace("'}}",'')),
        phone=MappingField(mapping=['dic','div class=[nap]','div class=[row]','div class=[col-md-9]','div class=[row]','div class=[col-xs-12, col-sm-6, col-md-5, hidden-xs]','div class=[c-phone, c-phone-main]','div class=[c-phone-number-wrapper, c-phone-main-number-wrapper]','div class=[c-phone-number, c-phone-main-number]'],
                           value_transform = lambda x : x.split("id=telephone': '")[-1].replace("'}}",'')),
        store_number=MissingField(),#MappingField(mapping=['id']),
        hours_of_operation=MappingField(mapping=['dic','div class=[nap]','div class=[row]','div class=[col-md-9]','div class=[row]','div class=[col-xs-12, col-sm-6, col-md-7, hidden-xs]'],
                                        value_transform = pretty_hours),
        location_type=MissingField(),#MappingField(mapping=['properties','features'], is_required = False)
    )

    pipeline = SimpleScraperPipeline(scraper_name='cititrends.com',
                                     data_fetcher=fetch_data,
                                     field_definitions=field_defs,
                                     log_stats_interval=5)

    pipeline.run()

if __name__ == "__main__":
    scrape()
