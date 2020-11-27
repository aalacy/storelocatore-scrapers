from sgscrape.simple_scraper_pipeline import *
from sgscrape import simple_network_utils as net_utils
from sgscrape import simple_utils as utils
from sgrequests import SgRequests
from sglogging import sglog
from bs4 import BeautifulSoup as b4
import json

def para(k):
    
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'}
    url = 'https://www.first.bank/'+k['NodeAliasPath']
    session = SgRequests()
    son = session.get(url, headers = headers).text
    soup = b4(son, 'lxml')
    final = ''
    try:
        hours = soup.find('div',{'class':'location-content-rich-text'}).stripped_strings
        for i in hours:
            if 'ours' in i:
                final = final + i + ': '
            elif 'day' in i:
                final = final + i + '; '
            else:
                print('HOPAAAAA',i)
    except:
        final = '<MISSING>'
    
            
    k['LobbyHours']['Days'].append(final)

    return k

def fetch_data():
    logzilla = sglog.SgLogSetup().get_logger(logger_name='Scraper')
    url = "https://www.first.bank/ZagLocationsApi/Locations/Search"
    headers = {
                'User-Agent' : 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36'
                ,'content-type': 'application/json'}
    #payload just for visualisation, actual payload sent as string below
    payload = {
        "Name":"St. Louis, MO",
        "Radius":50000,
        "Latitude":38.6270025,
        "Longitude":-90.19940419999999,
        "Connectors":{
            "Website":{
                "icon":"branch.png",
                "zIndex":10000,
                "selected":True,
                "filters":{
                    "BranchAtm":False,
                    "BranchItm":False,
                    "BranchNightDrop":False,
                    "BranchSafeDeposit":False,
                    "BranchDriveThrough":False,
                    "BranchSaturday":False,
                    "BranchAppointment":False
                    }
                },
            "Hla":{
                "icon":"hla.png",
                "zIndex":9999,
                "selected":True}
            },
        "OrderBy":"Distance",
        "CurrentPage":"/About/Locations"
        }
    #payload below
    payload = '{"Name":"St. Louis, MO","Radius":50000,"Latitude":38.6270025,"Longitude":-90.19940419999999,"Connectors":{"Website":{"icon":"branch.png","zIndex":10000,"selected":true,"filters":{"BranchAtm":false,"BranchItm":false,"BranchNightDrop":false,"BranchSafeDeposit":false,"BranchDriveThrough":false,"BranchSaturday":false,"BranchAppointment":false}},"Hla":{"icon":"hla.png","zIndex":9999,"selected":true}},"OrderBy":"Distance","CurrentPage":"/About/Locations"}'
    #payload above
    session = SgRequests()
    son = session.post(url, headers = headers, data = payload).text
    son = son.replace('\\"','"').replace("'",'').replace('"[','[').replace(']"',']')
    son = json.loads(son)

    nohours = []
    for i in son:
        try:
            i['LobbyHours']['Days'] = i['LobbyHours']['Days']
            yield i
        except:
            i['LobbyHours'] = {}
            i['LobbyHours']['Days'] = []
            nohours.append(i)

    lize = utils.parallelize(
                search_space = nohours,
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
    days = ['Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday']
    h = []
    if len(k) == 1:
        return k[0].replace(u'\xa0', u' ')
    
    for i in k:
        day = days[i['Name']]
        closed = i['Closed']
        opening = str(i['Open'].split('T')[1])
        closing = str(i['Close'].split('T')[1])
        if not closed:
            h.append(day+': '+opening+'-'+closing)
        else:
            h.append(day+': Closed')
    return '; '.join(h)

def scrape():
    url="https://www.first.bank/"
    field_defs = SimpleScraperPipeline.field_definitions(
        locator_domain = ConstantField(url),
        page_url = MappingField(mapping=['NodeAliasPath'], value_transform = lambda x : 'https://www.first.bank/'+x),
        location_name = MappingField(mapping=['Name'], value_transform = lambda x : x.replace('None','<MISSING>')),
        latitude = MappingField(mapping=['Latitude']),
        longitude = MappingField(mapping=['Longitude']),
        street_address = MultiMappingField(mapping=[['Address1'],['Address2']], multi_mapping_concat_with = ', ', value_transform = fix_comma),
        city = MappingField(mapping=['City'], value_transform = lambda x : x.replace('None','<MISSING>')),
        state = MappingField(mapping=['State'], value_transform = lambda x : x.replace('None','<MISSING>')),
        zipcode = MappingField(mapping=['ZipCode'], value_transform = lambda x : x.replace('None','<MISSING>'), is_required = False),
        country_code = MissingField(),
        phone = MappingField(mapping=['Phone'], value_transform = lambda x : x.replace('None','<MISSING>') , is_required = False),
        store_number = MappingField(mapping=['Id']),
        hours_of_operation = MappingField(mapping=['LobbyHours','Days'], raw_value_transform = pretty_hours, is_required = False),
        location_type= MappingField(mapping=['LocationType'], is_required = False)
    )

    pipeline = SimpleScraperPipeline(scraper_name='first.bank',
                                     data_fetcher=fetch_data,
                                     field_definitions=field_defs,
                                     log_stats_interval=15)

    pipeline.run()

if __name__ == "__main__":
    scrape()
