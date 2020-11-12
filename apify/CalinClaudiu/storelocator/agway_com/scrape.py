from sgscrape.simple_scraper_pipeline import *
from sgscrape import simple_network_utils as net_utils

def isagway(data, x):
    it = '<MISSING>'
    url = '<MISSING>'
    name = '<MISSING>'
    x = list(x['p'].keys())
    name = data.split('name=',1)[1].split('address',1)[0]
    try:
        url = x[-1].split('href=',1)[1].split(' target',1)[0]
    except:
        pass
    if 'gway' in name or 'gway' in url:
            it = 'Agway'
    return name ,it , url
        
        

def parse_hours(hours):
    parsed = []
    try:
        for i in hours['div class=[col-sm-12, flexbox-list]']['div class=[col-sm-6, flexbox-media]']['div class=[location-hours, card-plain]']['ul class=[list-unstyled]']:
            parsed.append(str(str(hours['div class=[col-sm-12, flexbox-list]']['div class=[col-sm-6, flexbox-media]']['div class=[location-hours, card-plain]']['ul class=[list-unstyled]'][i]['li'])+" " +str(hours['div class=[col-sm-12, flexbox-list]']['div class=[col-sm-6, flexbox-media]']['div class=[location-hours, card-plain]']['ul class=[list-unstyled]'][i]['div class=[pull-right]']['div class=[pull-right]'])))
    except:
        parsed.append('<MISSING>')
    return '; '.join(parsed)
        
        
def fetch_data():
    url = 'https://www.agway.com/locations'
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'}
    main = net_utils.fetch_xml(request_url = url,
                                root_node_name = 'body',
                                location_node_name = 'a',
                                location_node_properties = {'class':'page-link', 'rel':False},
                                headers = headers)
    
    pages = ['?page=1']
    for i in main:
        pages.append(str(i).split('locations')[1].split("':")[0])

    for i in pages:
        infos = net_utils.fetch_xml(request_url = url+i,
                                root_node_name = 'body',
                                location_node_name = 'div',
                                location_node_properties = {'class':'col-sm-12 location-wrap'},
                                headers = headers)
        
        coords = net_utils.fetch_xml(request_url = url+i,
                                root_node_name = 'body',
                                location_node_name = 'span',
                                location_node_properties = {'id':'map_data', 'class':'gm-maps-data'},
                                headers = headers)
        coords = next(coords)
        coords = list(coords)
        for j in coords:
            store = {}
            x = next(infos)
            h = parse_hours(x)
            store['hours']=h
            (store['name'],store['type'],store['purl']) = isagway(j,x['div class=[col-sm-12, flexbox-list]']['div class=[flexbox-media, col-sm-6]']['div class=[location-address, card-plain]'])
            store['data']=j
            store['dic']=x
            if store['purl']=='<MISSING>':
                store['purl'] = list(store['dic']['div class=[col-sm-12]']['div class=[location-title]']['h2'])[0].split('href=',1)[1]
            yield store
                                

    
def scrape():
    url="https://www.agway.com/"
    field_defs = SimpleScraperPipeline.field_definitions(
        locator_domain=ConstantField(url),
        page_url=MappingField(mapping=['purl']),
        location_name=MappingField(mapping=['name']),
        latitude=MappingField(mapping=['data'] , value_transform = lambda x : x.split('latitude=',1)[1].split(' ',1)[0]),
        longitude=MappingField(mapping=['data'] , value_transform = lambda x : x.split('longitude=',1)[1].split(' ',1)[0]),
        street_address=MappingField(mapping=['data'] , value_transform = lambda x : x.split('address=',1)[1].split(' address2',1)[0]),
        city=MappingField(mapping=['data'] , value_transform = lambda x : x.split('city=',1)[1].split(' ',1)[0]),
        state=MappingField(mapping=['data'] , value_transform = lambda x : x.split('state=',1)[1].split(' ',1)[0]),
        zipcode=MappingField(mapping=['data'] , value_transform = lambda x : x.split('zip=',1)[1].split(' ',1)[0]),
        country_code=MissingField(),
        phone=MappingField(mapping=['data'] , value_transform = lambda x : x.split('phone=',1)[1].split(' tollfree',1)[0]),
        store_number=MappingField(mapping=['dic','div class=[col-sm-12]','div class=[location-title]','h2'], value_transform = lambda x : x.split('/locations/',1)[1].split('/',1)[0]),
        hours_of_operation=MappingField(mapping=['hours']),
        location_type=MappingField(mapping=['type'])
    )

    pipeline = SimpleScraperPipeline(scraper_name='agway.com',
                                     data_fetcher=fetch_data,
                                     field_definitions=field_defs,
                                     log_stats_interval=5)

    pipeline.run()

if __name__ == "__main__":
    scrape()
