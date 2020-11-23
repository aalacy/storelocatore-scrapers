from sgscrape.simple_scraper_pipeline import *
from sgscrape import simple_network_utils as net_utils
from sgscrape import simple_utils as utils
from sgrequests import SgRequests
from sglogging import sglog
from bs4 import BeautifulSoup as b4
import json

def para(url):

    if 'locations.tacojohns.com' not in url:
        url = 'https://locations.tacojohns.com/'+url

    headers = {
                'User-Agent' : 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36'        }
    session = SgRequests()
    son = session.get(url, headers = headers)
    soup = b4(son.text , 'lxml')

    data = soup.find('div',{'class':'location-information'})
    
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
        k['Name'] = data.find('div',{'itemprop':'name'}).find('span').text.strip()
    except:
        k['Name'] = '<MISSING>'
        
    try:
        k['Address'] = data.find('span',{'class':'c-address-street-1'}).text.strip()
    except:
        k['Address'] = '<MISSING>'

    try:
        k['Address'] = k['Address'] +' '+ data.find('span',{'class':'c-address-street-2'}).text.strip()
    except:
        k['Address'] = k['Address']
        
    try:
        k['City'] = data.find('span',{'itemprop':'addressLocality'}).text.strip()
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
        k['OpenHours'] = data.find('div',{'class':lambda x : x and 'js-location-hours' in x,'data-days':True,'data-showopentoday':True,'data-highlighttoday':True})['data-days']
        k['OpenHours'] = json.loads('{"days":'+k['OpenHours']+'}')
    except:
        k['OpenHours'] = '<MISSING>'
            
    try:
        k['IsActive'] = soup.find('span',{'class':'geomodifier'}).text.strip()
        if 'Open' in k['IsActive'] or 'OPEN' in k['IsActive'] or 'Soon' in k['IsActive'] or 'soon' in k['IsActive'] or 'closed' in k['IsActive'] or 'Close' in k['IsActive']:
            k['IsActive'] = k['IsActive']
        else:
            k['IsActive'] = '<MISSING>'
        
    except:
        k['IsActive'] = '<MISSING>'
            
    try:
        k['Country'] = data.find('abbr',{'itemprop':'addressCountry'}).text.strip()

    except:
        k['Country'] = '<MISSING>'
        
    return k

def fetch_data():
    logzilla = sglog.SgLogSetup().get_logger(logger_name='Scraper')
    url = "https://locations.tacojohns.com/index.html"
    headers = {
                'User-Agent' : 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36'        }
    session = SgRequests()
    son = session.get(url, headers = headers)
    soup = b4 (son.text, 'lxml')
    states = []
    cities = []
    stores = []


    logzilla.info(f'Grabbing state links')
    for i in soup.find('div',{'class':'c-directory-list-content-wrapper'}).find_all('a',{'class':'c-directory-list-content-item-link'}):
        count = i['href'].count('/')
        if count == 0:
            states.append(i['href'])
        elif count == 1:
            cities.append(i['href'])
        elif count > 1:
            stores.append(i['href'])
    url = 'https://locations.tacojohns.com/'
    logzilla.info(f'Grabbing city links')
    for i in states:
        son = session.get(url+i, headers = headers)
        soup = b4(son.text, 'lxml')
        for j in soup.find('div',{'class':'c-directory-list-content-wrapper'}).find_all('a',{'class':'c-directory-list-content-item-link'}):
            count = j['href'].count('/')
            if count == 1:
                cities.append(j['href'])
            elif count >1:
                stores.append(j['href'])

    logzilla.info(f'Grabbing store links')

    for i in cities:
        son = session.get(url+i, headers = headers)
        soup = b4(son.text, 'lxml')
        for j in soup.find('',{'class':lambda x : x and x.startswith('directory-container')}).find_all('a',{'class':lambda x : x and x.startswith('c-location-grid-item-link'),'href':True,'title':True,'data-yext-tracked':True}):
            stores.append(j['href'])

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
    url="https://www.tacojohns.com/"
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

    pipeline = SimpleScraperPipeline(scraper_name='tacojohns.com',
                                     data_fetcher=fetch_data,
                                     field_definitions=field_defs,
                                     log_stats_interval=15)

    pipeline.run()

if __name__ == "__main__":
    scrape()
