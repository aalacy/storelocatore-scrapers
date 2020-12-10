from sgscrape.simple_scraper_pipeline import *
from sgscrape import simple_network_utils as net_utils
from sgscrape import simple_utils as utils
from sglogging import sglog
from sgrequests import SgRequests
from bs4 import BeautifulSoup

def parse(soup):
    k = {}
    
    k['url'] = "<MISSING>"
    try:
        k['name'] = soup.find('a',{'class':'store-name'}).text
    except:
        k['name'] = "<MISSING>"
        
    try:
        k['lat'] = soup.find('a',{'href':lambda x : x and x.startswith('https://www.google.com/maps/dir/'),'class':'block-link','role':'heading'})['href'].rsplit('/',1)[-1].split(',')[0]
        k['lng'] = soup.find('a',{'href':lambda x : x and x.startswith('https://www.google.com/maps/dir/'),'class':'block-link','role':'heading'})['href'].rsplit('/',1)[-1].split(',')[1]
    except:
        k['lat'] = "<MISSING>"
        k['lng'] = "<MISSING>"
        
    try:
        k['address'] = list(soup.find('div',{'class':'store-address'}).stripped_strings)
        k['address'] = k['address'][0]
                              
    except:
        k['address'] = "<MISSING>"
        
    try:
        k['city'] = list(soup.find('div',{'class':'store-address'}).stripped_strings)
        k['city'] = k['city'][1].split(',')[0]
    except:
        k['city'] = "<MISSING>"
        
    try:
        k['state'] = list(soup.find('div',{'class':'store-address'}).stripped_strings)
        k['state'] = k['state'][1].split(',')[-1].split(' ')[-2]
    except:
        k['state'] = "<MISSING>"
        
    try:
        k['zip'] = list(soup.find('div',{'class':'store-address'}).stripped_strings)
        k['zip'] = k['zip'][1].split(',')[-1].split(' ')[-1]
    except:
        k['zip'] = "<MISSING>"
        
    try:
        k['country'] = 'US'
    except:
        k['country'] = "<MISSING>"
        
    try:
        k['phone'] = soup.find('a',{'class':'store-phone'}).text
    except:
        k['phone'] = "<MISSING>"
        
    try:
        k['id'] = soup.find('div',{'class':'store-number'}).text
    except:
        k['id'] = "<MISSING>"

    try:
        j = []
        k['hours'] = list(soup.find('div',{'class':'store-list-row-item-col02'}).stripped_strings)
        if len(k['hours'])>1:
            k['hours'].pop(-1)
        k['hours'] = '; '.join(k['hours'])
    except:
        k['hours'] = "<MISSING>"
    k['type'] = "<MISSING>"
    return k

def fetch_data():
    logzilla = sglog.SgLogSetup().get_logger(logger_name='Scraper')
    url = "https://www.henhouse.com/store-locator/"
    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36'
    }
    session = SgRequests()
    son = session.get(url, headers = headers)
    soup = BeautifulSoup(son.text , 'lxml')
    soup = soup.find('div',{'id':'store-listing-rows'})
    for i in soup.find_all('div',{'class':'store-list-row-container store-bucket filter-rows'}):
        yield parse(i)

    logzilla.info(f'Finished grabbing data!!')

def nice_hours(x):
    hours = []
    x = x.split('\n')
    for i in x:
        if bool(re.search(r'\d', i)) == 1:
            hours.append(i)


    return '; '.join(hours)

def scrape():
    url="https://www.henhouse.com/"
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

    pipeline = SimpleScraperPipeline(scraper_name='henhouse.com',
                                     data_fetcher=fetch_data,
                                     field_definitions=field_defs,
                                     log_stats_interval=25)

    pipeline.run()

if __name__ == "__main__":
    scrape()
