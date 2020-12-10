from sgscrape.simple_scraper_pipeline import *
from sgscrape import simple_network_utils as net_utils
from sgscrape import simple_utils as utils
from sglogging import sglog
from sgrequests import SgRequests
from bs4 import BeautifulSoup

def para(url):
    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36'
    }
    session = SgRequests()
    r = session.get(url, headers = headers)
    k = {}
    soup = BeautifulSoup(r.text,'lxml')
    data = soup.find('div',{'class':'main-content'})
    k['url'] = url
    try:
        k['name'] = data.find('div',{'class':'medium-8 columns'}).find('h1').text
    except:
        k['name'] = "<MISSING>"
    try:
        k['address'] = list(data.find('div',{'class':'medium-4 columns'}).find('p').stripped_strings)
        k['address'] = k['address'][1]         
    except:
        k['address'] = "<MISSING>"
        
    try:
        k['city'] = list(data.find('div',{'class':'medium-4 columns'}).find('p').stripped_strings)
        k['city'] = k['city'][-1].split(',')[0]
    except:
        k['city'] = "<MISSING>"
        
    try:
        k['state'] = list(data.find('div',{'class':'medium-4 columns'}).find('p').stripped_strings)
        k['state'] = k['state'][-1].split(',')[1].split(' ')[-2]
    except:
        k['state'] = "<MISSING>"
        
    try:
        k['zip'] = list(data.find('div',{'class':'medium-4 columns'}).find('p').stripped_strings)
        k['zip'] = k['zip'][-1].split(',')[1].split(' ')[-1]
    except:
        k['zip'] = "<MISSING>"
        
    try:
        k['country'] = 'US'
    except:
        k['country'] = "<MISSING>"
        
    try:
        k['phone'] = list(data.find('div',{'class':'medium-4 columns'}).find('p').findNext('p').stripped_strings)
        k['phone'] = k['phone'][1]
    except:
        k['phone'] = "<MISSING>"
        
    try:
        k['id'] = soup.find('link',{'rel':'alternate','type':'application/json','href':True})['href'].rsplit('/',1)[-1]
    except:
        k['id'] = "<MISSING>"

    try:
        k['hours'] = list(data.find('ul',{'class':'hours'}).stripped_strings)
        k['hours'] = '; '.join(k['hours']).replace(':;',':')
    except:
        k['hours'] = "<MISSING>"

    k['type'] = "<MISSING>"
    return k

    
def fetch_data():
    logzilla = sglog.SgLogSetup().get_logger(logger_name='Scraper')
    url = "https://www.freshandnaturalfoods.com/fnf-locations/"
    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36'
    }
    links = []
    session = SgRequests()
    son = session.get(url,headers=headers)
    soup = BeautifulSoup(son.text, 'lxml')
    soup = soup.find('div',{'class':'fnf-locations'})
    for i in soup.find_all('a',{'class':'button'}):
        links.append(i['href'])
    j = utils.parallelize(
                search_space = links,
                fetch_results_for_rec = para,
                max_threads = 10,
                print_stats_interval = 10
                )
    for i in j:
        yield i
    logzilla.info(f'Finished grabbing data!!')


def scrape():
    url="https://www.freshandnaturalfoods.com"
    field_defs = SimpleScraperPipeline.field_definitions(
        locator_domain = ConstantField(url),
        page_url=MappingField(mapping=['url']),
        location_name=MappingField(mapping=['name']),
        latitude=MissingField(),
        longitude=MissingField(),
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

    pipeline = SimpleScraperPipeline(scraper_name='freshandnaturalfoods.com',
                                     data_fetcher=fetch_data,
                                     field_definitions=field_defs,
                                     log_stats_interval=25)

    pipeline.run()

if __name__ == "__main__":
    scrape()
