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

    country = xml_result.find('html',attrs = {'lang':True}).get('lang')

    root_node = xml_result.find(root_node_name)

    location_nodes = root_node.find_all(location_node_name, location_node_properties)

    for location in location_nodes:
        yield {'dic' : location_parser(location),
               'requrl' : request_url,
               'country': country}


def fetch_data():
    url = "https://www.cellphonerepair.com/locations/"
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
           }
 
    states = net_utils.fetch_xml(
        root_node_name='body',
        location_node_name='div',
        location_node_properties={'class':'state-loc-block'},
        request_url=url,
        headers=headers)
    stores = {'state':[],'city':[],'store':[]}
    for j in states:
        #https://www.cellphonerepair.com/cpr-canada/
        link = ''.join(list(j)).split('href=')[1].split('/')[0:-1]
        link[0]=link[0]
        link = '/'.join(link)
        if link.split('/')[-1]!='cpr-canada':
            stores['state'].append(link)
    #building states list
    url = "https://www.cellphonerepair.com"
    j = utils.parallelize(search_space = stores['state'],
                          fetch_results_for_rec = lambda x : net_utils.fetch_xml(
                                                              root_node_name='body',
                                                              location_node_name='div',
                                                              location_node_properties={'class':'store'},
                                                              request_url=x,
                                                              headers=headers),
                          max_threads = 12,
                          print_stats_interval = 12)
    for i in j:
        for h in i:
            if 'Coming Soon' in str(json.dumps(h)):
                pass
            else:
                link = list(h)[0].split('a href=')[1]
                link = url + link
                stores['store'].append(link)

    
    j = utils.parallelize(
                search_space = stores['store'],
                fetch_results_for_rec = lambda x : fetch_axml(
                                                    root_node_name='body',
                                                    location_node_name='div',
                                                    location_node_properties={'itemtype':'http://schema.org/LocalBusiness'},
                                                    request_url=x,
                                                    headers=headers),
                max_threads = 15,
                print_stats_interval = 15)
    for i in j:
        for h in i:
            yield h


def pretty_hours(x):

    api = "https://cprapi.fpsdv.com/wp-json/cprfe/v1/working-hours/?location_id="#900735
    try:
        x = x.split('var locID = ')[1].split(';')[0]
        headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
               }
        son = net_utils.fetch_html(
            request_url = api + x,
            headers = headers
            )
        for i in son:
            x = i
        x = x['p']['p'].split('"regularHours":[')[1].split('],"holidayHours"')[0]
        x = '{"hours":['+x+']}'
        son = json.loads(x)
        x = []
        for i in son['hours']:
            x.append(i['schema'])
        x = ', '.join(x)
    except:
        return 'Mo Closed, Tu Closed, Wed Closed, Thu Closed, Fri Closed, Sat Closed, Sun Closed'
    return x
def store_no(x):
    try:
        x = x.split('var locID = ')[1].split(';')[0]
    except:
        return '<MISSING>'    
    return x
    
def scrape():
    url="https://www.cellphonerepair.com/"
    field_defs = SimpleScraperPipeline.field_definitions(
        locator_domain=ConstantField(url),
        page_url=MappingField(mapping=['requrl']),
        location_name=MappingField(mapping=['dic'], value_transform = lambda x : x.split('meta itemprop=name content=',1)[-1].split("':")[0]),
        latitude=MappingField(mapping=['dic','div itemprop=geo itemscope= itemtype=http://schema.org/GeoCoordinates'], value_transform = lambda x : x.split('itemprop=latitude content=')[1].split("'")[0], part_of_record_identity = True),
        longitude=MappingField(mapping=['dic','div itemprop=geo itemscope= itemtype=http://schema.org/GeoCoordinates'], value_transform = lambda x : x.split('itemprop=longitude content=')[1].split("'")[0], part_of_record_identity = True),
        street_address=MappingField(mapping=['dic','div itemprop=address itemscope= itemtype=http://schema.org/PostalAddress'], value_transform = lambda x : x.split('itemprop=streetAddress content=')[1].split(',')[0]),
        city=MappingField(mapping=['dic','div itemprop=address itemscope= itemtype=http://schema.org/PostalAddress'], value_transform = lambda x : x.split('itemprop=addressLocality content=')[1].split("'")[0]),
        state=MappingField(mapping=['dic','div itemprop=address itemscope= itemtype=http://schema.org/PostalAddress'], value_transform = lambda x : x.split('itemprop=addressRegion content=')[1].split("'")[0]),
        zipcode=MappingField(mapping=['dic','div itemprop=address itemscope= itemtype=http://schema.org/PostalAddress'], value_transform = lambda x : x.split('itemprop=postalCode content=')[1].split("'")[0]),
        country_code=MappingField(mapping=['country'], value_transform = lambda x : x.split('-')[-1]),
        phone=MappingField(mapping=['dic'], value_transform = lambda x : x.split('a href=tel:')[1].split(" tabindex=")[0], is_required = False),
        store_number=MappingField(mapping=['dic','div id=page class=[site]','div id=content class=[site-content]'], value_transform = store_no, part_of_record_identity = True),
        hours_of_operation=MappingField(mapping=['dic','div id=page class=[site]','div id=content class=[site-content]'], value_transform = pretty_hours),
        location_type=MissingField(),#MappingField(mapping=['properties','features'], is_required = False)
    )

    pipeline = SimpleScraperPipeline(scraper_name='cellphonerepair.com',
                                     data_fetcher=fetch_data,
                                     field_definitions=field_defs,
                                     log_stats_interval=10)

    pipeline.run()

if __name__ == "__main__":
    scrape()
