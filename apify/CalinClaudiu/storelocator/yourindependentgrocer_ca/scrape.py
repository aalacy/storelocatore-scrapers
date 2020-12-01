from sgscrape.simple_scraper_pipeline import *
from sgscrape import simple_network_utils as net_utils
from sgscrape import simple_utils as utils
from sgrequests import SgRequests
from sglogging import sglog
import json
def determine(banner,ide):
    link = {
        'independentcitymarket':'https://www.independentcitymarket.ca/',
        'superstore':'https://realcanadiansuperstore.ca/',
        'provigo':'https://provigo.ca/',
        'valumart':'https://valumart.ca/',
        'nofrills':'https://nofrills.ca/',
        'independent':'https://yourindependentgrocer.ca/',
        'rass':'https://atlanticsuperstore.ca/',
        'loblaw':'https://www.loblaws.ca/',
        'dominion':'https://joefresh.com/',
        'zehrs':'https://www.zehrs.ca/',
        'extrafoods':'https://www.extrafoods.ca/',
        'fortinos':'https://www.fortinos.ca/',
        'maxi':'https://maxi.ca/',
        'wholesaleclub':'https://www.wholesaleclub.ca/'
        }
    return link[banner], link[banner]+'store-locator/details/'+ide

def para(k):
    session = SgRequests()
    ban = k['storeBannerId']
    ide = k['storeId']
    backup = k
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
               'Site-Banner' : ban}
    k = session.get('https://www.loblaws.ca/api/pickup-locations/'+k['storeId'], headers=headers).json()
    
    k['domain'], k['page_url'] = determine(ban,ide)
    try:
        k['hours'] = '; '.join([str(i['day']+': '+i['hours']) for i in k['storeDetails']['storeHours']])
    except:
        k = backup
        k['hours'] = k['openNowResponseData']['hours']
        k['storeDetails'] = {}
        k['storeDetails']['phoneNumber'] = k['contactNumber']
    k['storeBannerId'] = ban
    k['storeId'] = ide

    return k
                           
def fetch_data():
    logzilla = sglog.SgLogSetup().get_logger(logger_name='Scraper')
    url = "https://www.loblaws.ca/api/pickup-locations?"
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'}
    session = SgRequests()
    son = session.get(url, headers = headers).json()
    #I already have 99% of data, however some stores don't have their phone numbers in this main json. Must make individual requests.
    #sub-request https://www.loblaws.ca/api/pickup-locations/3957
    #only important header example : Site-Banner: nofrills
    #banners = {'independentcitymarket', 'superstore', 'provigo', 'valumart', 'nofrills', 'independent', 'rass', 'loblaw', 'dominion',
    #'zehrs', 'extrafoods', 'fortinos', 'maxi', 'wholesaleclub'}

    lize = utils.parallelize(
                search_space = son,
                fetch_results_for_rec = para,
                max_threads = 20,
                print_stats_interval = 20
                )
    for i in lize:
        yield i



def scrape():
    field_defs = SimpleScraperPipeline.field_definitions(
        locator_domain = MappingField(mapping=['domain']),
        page_url=MappingField(mapping=['page_url']),
        location_name=MappingField(mapping=['name']),
        latitude=MappingField(mapping=['geoPoint','latitude']),
        longitude=MappingField(mapping=['geoPoint','longitude']),
        street_address=MultiMappingField(mapping=[['address','line1'],['address','line2']], part_of_record_identity = True, multi_mapping_concat_with = ', ', value_transform = lambda x : x.replace(   'None','')),
        city=MappingField(mapping=['address','town'], value_transform = lambda x : x.replace('None','<MISSING>'), part_of_record_identity = True),
        state=MappingField(mapping=['address','region'], value_transform = lambda x : x.replace('None','<MISSING>'), part_of_record_identity = True),
        zipcode=MappingField(mapping=['address','postalCode'], value_transform = lambda x : x.replace('None','<MISSING>'), is_required = False),
        country_code=MappingField(mapping=['address','country'], value_transform = lambda x : x.replace('None','<MISSING>')),
        phone=MappingField(mapping=['storeDetails','phoneNumber'], value_transform = lambda x : x.replace('None','<MISSING>') , is_required = False),
        store_number=MappingField(mapping=['storeId']),
        hours_of_operation=MappingField(mapping=['hours'], value_transform = lambda x : x.replace('None','<MISSING>'), is_required = False),
        location_type=MappingField(mapping=['storeBannerId'], part_of_record_identity = True)
    )

    pipeline = SimpleScraperPipeline(scraper_name='Loblaws Family',
                                     data_fetcher=fetch_data,
                                     field_definitions=field_defs,
                                     log_stats_interval=15)

    pipeline.run()

if __name__ == "__main__":
    scrape()
