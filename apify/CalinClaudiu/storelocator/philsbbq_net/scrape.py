from sgscrape.simple_scraper_pipeline import *
from sgscrape import simple_network_utils as net_utils
from sgscrape import simple_utils as utils
from sglogging import sglog
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import json

def parse_store(x):
    k = {}
    if 'close' in x.text:
        k['type'] = 'Temporarily Closed'
        try:
            k['name'] = list(x.find('div',{'class': lambda x : x and 'location-info-holder' in x}).stripped_strings)[0]
        except:
            k['name'] = '<MISSING>'
        try:
            k['address']= x.find('a',{'class':'map-address'}).text
            if(k['address'].count(',')>0):
                k['city']=k['address'].split(',')[-2].strip()
                k['province']=''.join(k['address'].split(',')[-1].split(' ')[:-1])
                k['postalCode']=k['address'].split(',')[-1].split(' ')[-1]
                k['address']=k['address'].split(',')[0]
            elif (k['address'].count(',')==1):
                k['city']=k['address'].split('Blvd.')[-2].split(' ')[:-2].replace(',','')
                k['province']=k['address'].split('Blvd.')[-1].split(' ')[-2].replace(',','')
                k['postalCode']=k['address'].split('Blvd.')[-1].split(' ')[-1].replace(',','')
                k['address']=k['address'].split('Blvd.')[0]+'Blvd.'
        except:
            pass
        try:
            k['phone']= x.find('a',{'href':lambda x : x and x.startswith('tel:')}).text
        except:
            k['phone']='<MISSING>'
        try:
            k['hours'] = list(x.find('div',{'class': lambda x : x and 'location-info-holder' in x}).stripped_strings)
            h = []
            still = True
            for i in k['hours']:
                if 'Hours' in i:
                    still = False
                if 'Contact' in i:
                    still = True
                if still == False:
                    if any(j.isdigit() for j in i) or 'day' in i:
                        h.append(i)
            k['hours'] = '; '.join(h)
        except:
            k['hours'] = '<MISSING>'

            
    else:
        try:
            k['name']=list(x.find('div',{'class': lambda x : x and 'location-info-holder' in x}).stripped_strings)[0]
        except:
            k['name']='<MISSING>'
        try:
            k['address']= x.find('a',{'class':'map-address'}).text
            if(k['address'].count(',')==2):
                k['city']=k['address'].split(',')[-2].strip()
                k['province']=''.join(k['address'].split(',')[-1].split(' ')[:-1])
                k['postalCode']=k['address'].split(',')[-1].split(' ')[-1]
                k['address']=k['address'].split(',')[0]
            elif(k['address'].count(',')==1):
                k['city']=k['address'].split('Blvd.')[1].split(' ')[:-2]
                h = []
                for i in k['city']:
                    if not any(char.isdigit() for char in i):
                        h.append(i)
                k['city'] = ' '.join(h).replace(',','').strip()
                k['province']=k['address'].split('Blvd.')[-1].split(' ')[-2].replace(',','')
                k['postalCode']=k['address'].split('Blvd.')[-1].split(' ')[-1].replace(',','')
                k['address']=k['address'].split('Blvd.')[0]+'Blvd.'
        except:
            pass
        try:
            k['phone']=x.find('a',{'href':lambda x : x and x.startswith('tel:')}).text
        except:
            k['phone']= '<MISSING>'
        try:
            k['hours'] = list(x.find('div',{'class': lambda x : x and 'location-info-holder' in x}).stripped_strings)
            h = []
            still = True
            for i in k['hours']:
                if 'Hours' in i:
                    still = False
                if 'Contact' in i:
                    still = True
                if still == False:
                    if any(j.isdigit() for j in i) or 'day' in i:
                        h.append(i)
            k['hours'] = '; '.join(h)
        except:
            k['hours'] = '<MISSING>'
                    
            
        k['type']='<MISSING>'
    k['country'] = 'US'       
    return k

def fetch_data():
    logzilla = sglog.SgLogSetup().get_logger(logger_name='philsbbq')
    url = "https://philsbbq.net/san-diego-point-loma-phils-bbq-locations"
    #there's a chance this may change in the future.
    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36'
    }
    session = SgRequests()
    son = session.get(url, headers = headers)
    soup = BeautifulSoup(son.text, 'lxml')
    storse = soup.find('div',{'class':'col-md-12 party-offer'})
    for i in storse.find_all('div',{'class':True,'style':True}):
        yield parse_store(i)
    logzilla.info(f'Finished grabbing data!!')


def scrape():
    url="https://philsbbq.net/"
    field_defs = SimpleScraperPipeline.field_definitions(
        locator_domain = ConstantField(url),
        page_url=MissingField(),
        location_name=MappingField(mapping=['name']),
        latitude=MissingField(),
        longitude=MissingField(),
        street_address=MappingField(mapping=['address']),
        city=MappingField(mapping=['city'], is_required = False),
        state=MappingField(mapping=['province'], is_required = False),
        zipcode=MappingField(mapping=['postalCode'], is_required = False),
        country_code=MappingField(mapping=['country']),
        phone=MappingField(mapping=['phone'], is_required = False),
        store_number=MissingField(),
        hours_of_operation=MappingField(mapping=['hours'], is_required = False),
        location_type=MappingField(mapping=['type'], is_required = False)
    )

    pipeline = SimpleScraperPipeline(scraper_name='philsbbq.net',
                                     data_fetcher=fetch_data,
                                     field_definitions=field_defs,
                                     log_stats_interval=25,
                                     post_process_filter=lambda rec: rec.location_name() != 'Corporate Office')

    pipeline.run()

if __name__ == "__main__":
    scrape()
