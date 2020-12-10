from sgscrape.simple_scraper_pipeline import *
from sgscrape import simple_network_utils as net_utils
from sgscrape import simple_utils as utils
import json
from sgzip import DynamicGeoSearch, SearchableCountries
from sglogging import sglog
from sgrequests import SgRequests
import unicodedata
import re

def nice_address(x):
    j = ['','','','','','']
    try:
        j[0] = x.split('"thoroughfare">',1)[1].split('</div>')[0]
    except:
        j[0] = "<MISSING>"
    try:
        j[1] = x.split('"premise">',1)[1].split('</div>')[0]
    except:
        j[1] = ''
    try:
        j[5] = x.split('country-',1)[1].split('">')[0]
    except:
        j[5] = "<MISSING>"
    try:
        j[3] = x.split('"locality">',1)[1].split('</span>')[0]
    except:
        j[3] = "<MISSING>"
    try:
        j[4] = x.split('"state">',1)[1].split('</span> ')[0]
    except:
        j[4] = "<MISSING>"
    try:
        j[2] = x.split('"postal-code">',1)[1].split('</span>')[0]
    except:
        j[2] = "<MISSING>"
    return j

def fetch_data():
    logzilla = sglog.SgLogSetup().get_logger(logger_name='sgzip')
    url = "https://raisingcanes.com/sites/all/themes/raising_cane_s/locator/include/locationsNew.php?&lat="
    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36'
    }
    session = SgRequests()
    search = DynamicGeoSearch(country_codes=[SearchableCountries.USA])
    search.initialize()
    coord = search.next()
    identities = set()
    while coord:
        lat, long = coord
        son = r1 = session.get(url+str(lat)+"&lng="+str(long), headers = headers).json()
        result_lats = []
        result_longs = []
        result_coords = []
        topop = 0
        for idex ,i in enumerate(son['response']):
            i['parsed'] = []
            result_lats.append(i['geometry']['coordinates'][1])
            result_longs.append(i['geometry']['coordinates'][0])
            if ''.join(str(j) for j in i['geometry']['coordinates']) not in identities:
                identities.add(''.join(str(j) for j in i['geometry']['coordinates']))
                i['parsed'] = nice_address(i['properties']['gsl_addressfield'])
                yield i
            else:
                topop += 1
        result_coords = list(zip(result_lats,result_longs))
        logzilla.info(f'Coordinates remaining: {search.zipcodes_remaining()}; Last request yields {len(result_coords)-topop} stores.')
        search.update_with(result_coords)
        coord = search.next()
    logzilla.info(f'Finished grabbing data!!')

def fix_hours(x):
    h = []
    try:
        x = x.split('<br />')
        for i in x:
            if bool(re.search(r'\d', i))==True:
                h.append(i)
        h = '; '.join(h)
        h = h.split('<div')[0]
    except:
        pass
    x = h
    x = x.replace('\u200b','').replace('<p>','').replace('</p>','').replace('&nbsp;',' ')
    if x=='None':
        x='<MISSING>'
    return x.replace('\n',' ').lstrip().rstrip()

def scrape():
    url="https://raisingcanes.com"
    field_defs = SimpleScraperPipeline.field_definitions(
        locator_domain = ConstantField(url),
        page_url=MappingField(mapping=['properties','path'], value_transform = lambda x : x.split('href="')[1].split('">')[0]),
        location_name=MappingField(mapping=['properties','name'], value_transform = lambda x : x.replace('&#039;',"'")),
        latitude=MappingField(mapping=['geometry','coordinates',1]),
        longitude=MappingField(mapping=['geometry','coordinates',0]),
        street_address=MultiMappingField(mapping=[['parsed',0],['parsed',1]], multi_mapping_concat_with = ', '),
        city=MappingField(mapping=['parsed',3]),
        state=MappingField(mapping=['parsed',4]),
        zipcode=MappingField(mapping=['parsed',2], value_transform = lambda x : '02215' if x=='2215' else x ),
        #4    MA  617-358-5932  2215  INVALID_US_ZIP == Although scraped correctly, this check is not ignorable, it should start with a '0'
        country_code=MappingField(mapping=['parsed',5]),
        phone=MappingField(mapping=['properties','field_phone'], value_transform = lambda x : '<MISSING>' if x == 'None' else x),
        store_number=MappingField(mapping=['properties','name'], value_transform = lambda x : x.replace('&#039;',"'").split('#')[1]),
        hours_of_operation=MappingField(mapping=['hours'], value_transform = fix_hours, is_required = False),
        location_type=MappingField(mapping=['properties','field_unit_status'], value_transform = lambda x : '<MISSING>' if 'Open' in x else x)
    )

    pipeline = SimpleScraperPipeline(scraper_name='raisingcanes.com',
                                     data_fetcher=fetch_data,
                                     field_definitions=field_defs,
                                     log_stats_interval=15)

    pipeline.run()

if __name__ == "__main__":
    scrape()
