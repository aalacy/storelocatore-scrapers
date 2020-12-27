from sgscrape.simple_scraper_pipeline import *
from sgscrape import simple_network_utils as net_utils
from sgscrape import simple_utils as utils
from sgrequests import SgRequests
from sglogging import sglog
from bs4 import BeautifulSoup as b4
import json

def para(url):
    if 'https://stores.cartier.com/https' in url:
        url = url.replace('https://stores.cartier.com/https','https')
    headers = {
                'User-Agent' : 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36'        }
    session = SgRequests()
    son = session.get(url, headers = headers)
    soup = b4(son.text , 'lxml')

    data = soup.find('div',{'class':'NAP'})
    
    k = {}

    k['CustomUrl'] = url

    try:
        k['Latitude'] = data.find('meta',{'itemprop':'latitude'})['content']
    except:
        k['Latitude'] = '<MISSING>'
        
    try:
        k['Longitude'] = data.find('meta',{'itemprop':'longitude'})['content']
    except:
        k['Longitude'] = '<MISSING>'
        
    try:
        k['Name'] = data.find('span',{'class':'LocationName-geo'}).text.strip()
    except:
        k['Name'] = '<MISSING>'
        
    try:
        k['Address'] = data.find('meta',{'itemprop':'streetAddress'})['content'].strip()
    except:
        k['Address'] = '<MISSING>'
        
    try:
        k['City'] = data.find('span',{'class':'c-address-city'}).text.strip()
    except:
        k['City'] = '<MISSING>'
        
    try:
        k['State'] = data.find('abbr',{'itemprop':'addressRegion'}).text.strip()
    except:
        k['State'] = '<MISSING>'
        
    try:
        k['Zip'] = data.find('span',{'itemprop':'postalCode'}).text.strip()
    except:
        k['Zip'] = '<MISSING>'
        
    try:
        k['Phone'] = data.find('span',{'itemprop':'telephone'}).text.strip()
    except:
        k['Phone'] = '<MISSING>'
        
    try:
        k['OpenHours'] = data.find('div',{'class':lambda x : x and 'js-location-hours' in x,'data-days':True})['data-days']
        k['OpenHours'] = json.loads('{"days":'+k['OpenHours']+'}')
    except:
        k['OpenHours'] = '<MISSING>'
            
    try:
        k['IsActive'] = data.find('span',{'class':'LocationName-brand'}).text.strip()
    except:
        k['IsActive'] = '<MISSING>'
            
    try:
        k['Country'] = data.find('abbr',{'itemprop':'addressCountry'}).text.strip()

    except:
        k['Country'] = '<MISSING>'
        
    return k

def fetch_data():
    logzilla = sglog.SgLogSetup().get_logger(logger_name='Scraper')
    urlUS = "https://stores.cartier.com/en_us/united-states"
    urlCA = "https://stores.cartier.com/en_us/canada"
    headers = {
                'User-Agent' : 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36'        }
    session = SgRequests()
    for page in [urlUS,urlCA]:
        logzilla.info(f'\n\n')
        logzilla.info(f'Pulling data for {page.split("en_us/")[1]}')
        son = session.get(page, headers = headers)
        soup = b4 (son.text, 'lxml')
        states = []
        cities = []
        stores = []


        logzilla.info(f'Grabbing state links')
        for i in soup.find('div',{'class':'Main-content'}).find('div',{'class':'Directory-content'}).find_all('a',{'class':'Directory-listLink'}):
            count = i['href'].count('/')
            if count == 3:
                states.append(i['href'].replace('..','https://stores.cartier.com'))
            elif count == 4:
                cities.append(i['href'].replace('..','https://stores.cartier.com'))
            elif count > 4:
                stores.append(i['href'].replace('..','https://stores.cartier.com'))
        logzilla.info(f'Grabbing city links')
        for i in states:
            if 'https://stores.cartier.com/https' in i:
                i = i.replace('https://stores.cartier.com/https','https')
            son = session.get(i, headers = headers)
            soup = b4(son.text, 'lxml')
            for j in soup.find('div',{'class':'Main-content'}).find('div',{'class':'Directory-content'}).find_all('a',{'class':'Directory-listLink'}):
                count = j['href'].count('/')
                if count == 5:
                    cities.append(j['href'].replace('..','https://stores.cartier.com'))
                elif count >5:
                    stores.append(j['href'].replace('..','https://stores.cartier.com'))

        logzilla.info(f'Grabbing store links')

        for i in cities:
            if 'https://stores.cartier.com/https' in i:
                i = i.replace('https://stores.cartier.com/https','https')
            son = session.get(i, headers = headers)
            soup = b4(son.text, 'lxml')
            for j in soup.find_all('a',{'class':'Teaser-titleLink'}):
                stores.append('https://stores.cartier.com/en_us'+j['href'].split('en_us')[1])

        logzilla.info(f'Grabbing store data')
        
        lize = utils.parallelize(
                    search_space = stores,
                    fetch_results_for_rec = para,
                    max_threads = 10,
                    print_stats_interval = 10
                    )

        for i in lize:
            yield i
        
    logzilla.info(f'Finished grabbing data!!')

def fix_comma(x):
    h = []
    
    x = x.replace('None','')
    try:
        x = x.split(',')
        for i in x:
            if len(i)>1:
                h.append(i)
        h = ', '.join(h)
    except:
        h = x

    if(len(h)<2):
        h = '<MISSING>'

    return h

def pretty_hours(k):
    h = []
    
    if k != '<MISSING>':
        for i in k['days']:
            try:
                h.append(i['day']+': '+str(i['intervals'][0]['start'])+'-'+str(i['intervals'][0]['end']))
            except:
                h.append(i['day']+': '+str('Closed'))

        h = '; '.join(h)
    else:
        h = k

    return h

def scrape():
    url="https://www.cartier.com/"
    field_defs = SimpleScraperPipeline.field_definitions(
        locator_domain = ConstantField(url),
        page_url=MappingField(mapping=['CustomUrl']),
        location_name=MappingField(mapping=['Name'], value_transform = lambda x : x.replace('None','<MISSING>')),
        latitude=MappingField(mapping=['Latitude']),
        longitude=MappingField(mapping=['Longitude']),
        street_address=MappingField(mapping=['Address'], value_transform = fix_comma),
        city=MappingField(mapping=['City'], value_transform = lambda x : x.replace('None','<MISSING>')),
        state=MappingField(mapping=['State'], value_transform = lambda x : x.replace('None','<MISSING>')),
        zipcode=MappingField(mapping=['Zip'], value_transform = lambda x : x.replace('None','<MISSING>'), is_required = False),
        country_code=MappingField(mapping=['Country']),
        phone=MappingField(mapping=['Phone'], value_transform = lambda x : x.replace('None','<MISSING>') , is_required = False),
        store_number=MissingField(),
        hours_of_operation=MappingField(mapping=['OpenHours'], raw_value_transform = pretty_hours, is_required = False),
        location_type=MappingField(mapping=['IsActive']),
    )

    pipeline = SimpleScraperPipeline(scraper_name='cartier.com',
                                     data_fetcher=fetch_data,
                                     field_definitions=field_defs,
                                     log_stats_interval=15)

    pipeline.run()

if __name__ == "__main__":
    scrape()
