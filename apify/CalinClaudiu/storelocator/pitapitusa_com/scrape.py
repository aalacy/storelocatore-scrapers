from sgscrape.simple_scraper_pipeline import *
from sgscrape import simple_network_utils as net_utils
from sgscrape import simple_utils as utils
from sgrequests import SgRequests
import bs4
from bs4 import BeautifulSoup
import json

def gibjs(url):
    session = SgRequests()
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'}
    scriptjs = session.get(url, headers = headers)
    xml_result = BeautifulSoup(scriptjs.text, 'lxml')
    scriptjs = xml_result.find('script',{'src':lambda x : x and x.startswith('scripts/app-')})
    #scriptjs['src'] should be something like "scripts/app-4e41ab1928.js"
    
    return scriptjs['src']
    
def gibtoken(js):
    session = SgRequests()
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'}
    token = session.get("https://locations.pitapitusa.com/"+js, headers = headers)
    auth = token.text.split('.constant("API_TOKEN",',1)[1].split(')',1)[0]
    auth = auth.replace('"','').replace(' ','')
    
    return auth
    
def para(tup):
    session = SgRequests()
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'}
    headers['Authorization'] = tup[2]
    k = session.get(tup[1], headers = headers).json()
    k = k[0]
    k['index'] = tup[0]
    k['requrl'] = tup[1]
    yield k

def fetch_data():
    #api token in js of last script tag from https://locations.pitapitusa.com/site-map
    #api token in js link under .constant("API_TOKEN", "JQOUFDWGVOXGXEDG")
    #api call is https://momentfeed-prod.apigee.net/api/v2/llp/sitemap?auth_token=JQOUFDWGVOXGXEDG&country=US
    #location data from https://momentfeed-prod.apigee.net/api/llp.json?address=900+N+Highway+41&locality=Post+Falls&multi_account=false&pageSize=30&region=ID
    #location data requires header Authorization: JQOUFDWGVOXGXEDG
    logzilla = sglog.SgLogSetup().get_logger(logger_name='Pita*2')

    url = 'https://locations.pitapitusa.com/site-map/US/MT'
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'}

    logzilla.info(f'Finding js code to fetch auth token')
    js = gibjs(url)
    logzilla.info(f'Found JS code under: {js}')

    logzilla.info(f'Grabbing auth token')
    auth = gibtoken(js)
    logzilla.info(f'Found auth token as: {auth}')

    session = SgRequests()
    son = session.get("https://momentfeed-prod.apigee.net/api/v2/llp/sitemap?auth_token="+auth+"&country=US", headers = headers).json()

    logzilla.info(f'Building final request url list')
    for i in son['locations']:
        i['REQURL']=str("https://momentfeed-prod.apigee.net/api/llp.json?address="+i['store_info']['address'].replace(' ','+')+"&locality="+i['store_info']['locality'].replace(' ','+')+"&multi_account=false&pageSize=30&region="+i['store_info']['region'])
    
    par = utils.parallelize(
                search_space = [[counter,i['REQURL'],auth] for counter, i in enumerate(son['locations'])],
                fetch_results_for_rec = para,
                max_threads = 10,
                print_stats_interval = 10
                )
    for i in par:
        for j in i:
            j['dic'] = son['locations'][j['index']]
            yield j
    logzilla.info(f'Finished Grabbing data!')
def better_horas(x):
    days = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
    j = []
    if len(x)>1:
        x = x.split(';')
        x.pop()
        for i in days:
            x.append('Closed')
        k = dict(zip(days,x))
        for i in days:
            if 'Closed' not in k[i]:
                j.append(str(i+': '+k[i].split(',')[1]+':'+k[i].split(',')[2]))
            else:
                j.append(str(i+': '+k[i]))
    return '; '.join(j)
            
def scrape():
    url="https://pitapitausa.com/"
    field_defs = SimpleScraperPipeline.field_definitions(
        locator_domain=ConstantField(url),
        page_url=MappingField(mapping=['store_info','website']),
        location_name=MappingField(mapping=['meta','title']),
        latitude=MappingField(mapping=['store_info','latitude']),
        longitude=MappingField(mapping=['store_info','longitude']),
        street_address=MultiMappingField(mapping=[['store_info','address'],['store_info','address_extended'],['store_info','address_3']], multi_mapping_concat_with = ', '),
        city=MappingField(mapping=['store_info','locality']),
        state=MappingField(mapping=['store_info','region']),
        zipcode=MappingField(mapping=['store_info','postcode']),
        country_code=MappingField(mapping=['store_info','country']),
        phone=MappingField(mapping=['store_info','phone']),
        store_number=MappingField(mapping=['momentfeed_venue_id'], part_of_record_identity = True),
        hours_of_operation=MappingField(mapping=['store_info','store_hours'], value_transform = better_horas, is_required = False),
        location_type=MappingField(mapping=['open_or_closed'], is_required = False)
    )

    pipeline = SimpleScraperPipeline(scraper_name='pitapitausa.com',
                                     data_fetcher=fetch_data,
                                     field_definitions=field_defs,
                                     log_stats_interval=5)

    pipeline.run()

if __name__ == "__main__":
    scrape()
