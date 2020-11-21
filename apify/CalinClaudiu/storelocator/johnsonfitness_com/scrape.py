from sgscrape.simple_scraper_pipeline import *
from sgscrape import simple_network_utils as net_utils
from sgscrape import simple_utils as utils
from sgrequests import SgRequests
from sglogging import sglog
import json

def fetch_subpage(store_id):

    #https://www.johnsonfitness.com/Home/GetStoreInfo?store_id=6064
    #POST
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'}
    session = SgRequests()
    son = session.post('https://www.johnsonfitness.com/Home/GetStoreInfo?store_id='+str(store_id), headers = headers).json()
    
    return son


def do_hours(tab):
    tab = tab.replace('</tr>','').replace('</table>','')
    tab = tab.split('<tr class="hours">')
    days = [i.replace('</td>','').strip() for i in tab[0].split('<td>')]
    hours = [i.replace('</td>','').strip() for i in tab[1].split('<td>')]
    h = list(zip(days, hours))
    h.pop(0)
    hours = []
    for i in h:
        hours.append(str(i[0])+': '+str(i[1]))
    hours = '; '.join(hours)

    return hours

def get_id(soup):
    return soup.split('/StoreLocator/StoreProfile?store_id=')[1].split('"')[0]
    
def fetch_data():
    logzilla = sglog.SgLogSetup().get_logger(logger_name='Scraper')
    url = "https://www.johnsonfitness.com/StoreLocator/Index?lat=&lon=&id=locator-form"
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'}
    session = SgRequests()
    son = session.post(url, headers = headers)
    son = son.text
    son = son.replace('<!--','\n').replace('-->','\n')
    #bs4 just does not work here..
    son = son.split('<h2 class="showroom_type">')
    son[0] = son[0].split('<div class="single  odd">')[-1]
    son.pop()
    
    for i in son:
        store = {}
        ide = get_id(i)
        store = fetch_subpage(ide)
        store['hours'] = do_hours(i.split('<tr class="day">')[1])
        if ', Omaha' in store['Address1']:
            store['Address1'] = store['Address1'].split(', Omaha')[0]
        if ', Oklahoma City' in store['Address1']:
            store['Address1'] = store['Address1'].split(', Oklahoma City')[0]
        yield store

def scrape():
    url="https://www.johnsonfitness.com/"
    field_defs = SimpleScraperPipeline.field_definitions(
        locator_domain = ConstantField(url),
        page_url=MappingField(mapping=['FullURLPath']),
        location_name=MappingField(mapping=['Store_name']),
        latitude=MappingField(mapping=['Latitude']),
        longitude=MappingField(mapping=['Longitude']),
        street_address=MultiMappingField(mapping=[['Address1'],['Address2']], part_of_record_identity = True, multi_mapping_concat_with = ', ', value_transform = lambda x : x.replace(   'None','')),
        city=MappingField(mapping=['City'], value_transform = lambda x : x.replace('None','<MISSING>'), part_of_record_identity = True),
        state=MappingField(mapping=['State'], value_transform = lambda x : x.replace('None','<MISSING>'), part_of_record_identity = True),
        zipcode=MappingField(mapping=['Zip'], value_transform = lambda x : x.replace('None','<MISSING>'), is_required = False),
        country_code=MissingField(),
        phone=MappingField(mapping=['Phone_number'], value_transform = lambda x : x.replace('None','<MISSING>') , is_required = False),
        store_number=MappingField(mapping=['Store_id']),
        hours_of_operation=MappingField(mapping=['hours'], is_required = False),
        location_type=MissingField()
    )

    pipeline = SimpleScraperPipeline(scraper_name='johnsonfitness.com',
                                     data_fetcher=fetch_data,
                                     field_definitions=field_defs,
                                     log_stats_interval=15)

    pipeline.run()

if __name__ == "__main__":
    scrape()
