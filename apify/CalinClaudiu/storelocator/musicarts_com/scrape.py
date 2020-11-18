from sgscrape.simple_scraper_pipeline import *
from sgscrape import simple_network_utils as net_utils
from sgscrape import simple_utils as utils
from sgrequests import SgRequests
from bs4 import BeautifulSoup
from sglogging import sglog



def para(url):
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'}
    session = SgRequests()
    data = session.get(url,headers = headers)
    soup = BeautifulSoup(data.text , 'lxml')
    data = soup.find('div',{'class':'store-summary-container'})
    k = {}
    k['url'] = url
    try:
        k['name'] = data.find('h3',{'class':'store-name'})['content']
    except:
        k['name'] = "<MISSING>"
    try:
        k['lat'] = data.find('span',{'class':'coordinates'}).find('meta',{'itemprop':'latitude'})['content']
    except:
        k['lat'] = "<MISSING>"
        
    try:
        k['lng'] = data.find('span',{'class':'coordinates'}).find('meta',{'itemprop':'longitude'})['content']
    except:
        k['lng'] = "<MISSING>"
        
    try:
        k['address'] = data.find('span',{'class':'store-address1'}).text         
    except:
        k['address'] = "<MISSING>"
        
    try:
        k['city'] = data.find('span',{'class':'store-city'}).text.replace(',','')
    except:
        k['city'] = "<MISSING>"
        
    try:
        k['state'] = data.find('span',{'class':'store-state'}).text
    except:
        k['state'] = "<MISSING>"
        
    try:
        k['zip'] = data.find('span',{'class':'store-zip'}).text 
    except:
        k['zip'] = "<MISSING>"
        
    k['country'] = 'US'
        
    try:
        k['phone'] = data.find('a',{'href':lambda x : x and x.startswith('tel:')}).text
    except:
        k['phone'] = "<MISSING>"
        
    k['id'] = "<MISSING>"

    try:
        k['hours'] = '; '.join(list(data.find('table',{'id':'storehours','class':'store-hours-table'}).find('tbody').stripped_strings))
        k['hours'] = k['hours'].replace(':;',':')
    except:
        k['hours'] = "<MISSING>"

    try:
        k['type'] = data.find('div',{'class':'store-location'}).find('a',{'class':'loadMapDialog'})['data-contexttype']
    except:
        k['type'] = "<MISSING>"
    return k
    
def fetch_data():
    logzilla = sglog.SgLogSetup().get_logger(logger_name='musicarts')
    url = "https://stores.musicarts.com/"
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'}
    session = SgRequests()
    son = session.get(url, headers = headers)
    soup = BeautifulSoup(son.text, 'lxml')
    links = []
    states = []
    soup = soup.find('div', {'class':'state-listing clearfix'})
    for i in soup.find_all('ul'):
        for j in i.find_all('a',{'href':True}):
            logzilla.info(f'Building storelinks for {j.text}.')
            state = session.get(j['href'], headers = headers)
            soupy = BeautifulSoup(state.text, 'lxml')
            stores = soupy.find('div',{'class':'search-results'})
            for q in stores.find_all('a',{'href':True,'itemprop':'url'}):
                links.append(q['href'])
    logzilla.info(f'Found {len(links)} stores.')
    sublinks = utils.parallelize(
                search_space = links,
                fetch_results_for_rec = para,
                max_threads = 10,
                print_stats_interval = 10
                )
    k = {}
    for i in sublinks:
        yield i

    logzilla.info(f'Finished grabbing data!!')



def scrape():
    url="https://stores.musicarts.com/"
    field_defs = SimpleScraperPipeline.field_definitions(
        locator_domain = ConstantField(url),
        page_url=MappingField(mapping=['url']),
        location_name=MappingField(mapping=['name']),
        latitude=MappingField(mapping=['lat']),
        longitude=MappingField(mapping=['lng']),
        street_address=MappingField(mapping=['address']),
        city=MappingField(mapping=['city']),
        state=MappingField(mapping=['state']),
        zipcode=MappingField(mapping=['zip']),
        country_code=MappingField(mapping=['country']),
        phone=MappingField(mapping=['phone']),
        store_number=MappingField(mapping=['id']),
        hours_of_operation=MappingField(mapping=['hours']),
        location_type=MappingField(mapping=['type'])
    )

    pipeline = SimpleScraperPipeline(scraper_name='stores.musicarts.com',
                                     data_fetcher=fetch_data,
                                     field_definitions=field_defs,
                                     log_stats_interval=15)

    pipeline.run()

if __name__ == "__main__":
    scrape()
