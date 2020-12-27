from sgscrape.simple_scraper_pipeline import *
from sgscrape import simple_network_utils as net_utils
from sgscrape import simple_utils as utils
from sgrequests import SgRequests
from sglogging import sglog
from bs4 import BeautifulSoup as b4
import json
def nice_hours(k):
    h = []
    h.append(str('Monday: '+k['sl_hours_monday']))
    h.append(str('Tuesday: '+k['sl_hours_tuesday']))
    h.append(str('Wednesday: '+k['sl_hours_wednesday']))
    h.append(str('Thursday: '+k['sl_hours_thursday']))
    h.append(str('Friday: '+k['sl_hours_friday']))
    h.append(str('Saturday: '+k['sl_hours_saturday']))
    h.append(str('Sunday: '+k['sl_hours_sunday']))

    return '; '.join(h)
             
def fetch_data():
    logzilla = sglog.SgLogSetup().get_logger(logger_name='Scraper')
    url = "https://www.marbleslab.com/store-locator/"
    headers = {
                'User-Agent' : 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36'}
    
    session = SgRequests()
    son = session.get(url, headers = headers)
    soup = b4(son.text, 'lxml')
    scripts = soup.find_all('script',{'type':'text/javascript'})
    for i in scripts:
        if 'locations = [{"sl' in i.text:
            son = i.text
    son = '[{"'+son.split('locations = [{"')[1].split('"}];')[0]+'"}]'
    son = json.loads(son)
    
    for i in son:
        i['hours'] = nice_hours(i)
        if 'Soon' in i['sl_phone'] :
            i['type'] = 'Coming Soon'
            i['sl_phone'] = '<MISSING>'
        elif 'N/A' in i['sl_phone']:
            i['sl_phone'] = '<MISSING>'
            i['type'] = '<MISSING>'
        else:
             i['type'] = '<MISSING>'
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

    return h.replace('<br>','')


def scrape():
    url="https://www.marbleslab.com/"
    field_defs = SimpleScraperPipeline.field_definitions(
        locator_domain = ConstantField(url),
        page_url=MappingField(mapping=['sl_url'], is_required = False),
        location_name=MappingField(mapping=['sl_name'], value_transform = lambda x : x.replace('None','<MISSING>').replace('<br>','')),
        latitude=MappingField(mapping=['sl_latitude'], is_required = False),
        longitude=MappingField(mapping=['sl_longitude'], is_required = False),
        street_address=MappingField(mapping=['sl_address'], value_transform = fix_comma),
        city=MappingField(mapping=['sl_city'], value_transform = lambda x : x.replace('None','<MISSING>')),
        state=MappingField(mapping=['sl_state'], value_transform = lambda x : x.replace('None','<MISSING>')),
        zipcode=MappingField(mapping=['sl_zip'], value_transform = lambda x : x.replace('None','<MISSING>'), is_required = False),
        country_code=MappingField(mapping=['sl_country']),
        phone=MappingField(mapping=['sl_phone'], value_transform = lambda x : x.replace('None','<MISSING>') , is_required = False),
        store_number=MappingField(mapping=['sl_number']),
        hours_of_operation=MappingField(mapping=['hours'], is_required = False),
        location_type=MappingField(mapping=['type'], is_required = False)
    )

    pipeline = SimpleScraperPipeline(scraper_name='marbleslab.com',
                                     data_fetcher=fetch_data,
                                     field_definitions=field_defs,
                                     log_stats_interval=15)

    pipeline.run()

if __name__ == "__main__":
    scrape()
