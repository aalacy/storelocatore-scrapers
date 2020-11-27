from sgscrape.simple_scraper_pipeline import *
from sgscrape import simple_network_utils as net_utils
from sgscrape import simple_utils as utils
from sgrequests import SgRequests
from sglogging import sglog
import json

def fetch_data():
    logzilla = sglog.SgLogSetup().get_logger(logger_name='Scraper')
    url = "https://www.firstbanknj.com/_/api/branches/19.8968/-155.5828/50000"
    
    headers = {
                'User-Agent' : 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36'        }

    
    session = SgRequests()
    son = session.get(url, headers = headers).json()
    for k in son['branches']:
        yield k

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

def fix_semicolon(x):
    h = []
    
    x = x.replace('None','')
    try:
        x = x.split(';')
        for i in x:
            if len(i)>1:
                h.append(i)
        h = '; '.join(h)
    except:
        h = x

    return h.strip()

def pretty_hours(x):

    backup = x
    if 'and drive through' not in x:
        try:
            x = x.split('</div>')[1]
        except:
            x = '<MISSING>'
    else:
        try:
            x = x.split('</div>')[2]
        except:
            x = '<MISSING>'
    x = x.replace('<div>','').replace('<br>','; ').replace('\n','').replace('&amp;','&').replace('; ; ','; ').replace('</div>','')
    if 'N/A' in x:
        x = backup
        try:
            x = x.split('</b>')[1].split('<b>')[0]
            x = x.replace('<div>','').replace('<br>','; ').replace('\n','').replace('&amp;','&').replace('; ; ','; ').replace('</div>','')
        except:
            x = '<MISSING>'
        
    return fix_semicolon(x)
        
            
    
def scrape():
    url="https://www.firstbanknj.com/"
    field_defs = SimpleScraperPipeline.field_definitions(
        locator_domain = ConstantField(url),
        page_url=MissingField(),
        location_name=MappingField(mapping=['name'], value_transform = lambda x : x.replace('None','<MISSING>')),
        latitude=MappingField(mapping=['lat']),
        longitude=MappingField(mapping=['long']),
        street_address=MappingField(mapping=['address'], value_transform = fix_comma),
        city=MappingField(mapping=['city'], value_transform = lambda x : x.replace('None','<MISSING>')),
        state=MappingField(mapping=['state'], value_transform = lambda x : x.replace('None','<MISSING>')),
        zipcode=MappingField(mapping=['zip'], value_transform = lambda x : x.replace('None','<MISSING>'), is_required = False),
        country_code=MissingField(),
        phone=MappingField(mapping=['phone'], value_transform = lambda x : x.replace('None','<MISSING>') , is_required = False),
        store_number=MappingField(mapping=['id']),
        hours_of_operation=MappingField(mapping=['description'], value_transform = pretty_hours, is_required = False),
        location_type=MissingField()
    )

    pipeline = SimpleScraperPipeline(scraper_name='firstbanknj.com',
                                     data_fetcher=fetch_data,
                                     field_definitions=field_defs,
                                     log_stats_interval=15)

    pipeline.run()

if __name__ == "__main__":
    scrape()
