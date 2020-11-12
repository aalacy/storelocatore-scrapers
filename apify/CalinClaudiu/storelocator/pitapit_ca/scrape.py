from sgscrape.simple_scraper_pipeline import *
from sgscrape import simple_network_utils as net_utils
from sgscrape import simple_utils as utils
from sgzip import DynamicGeoSearch, SearchableCountries
from sglogging import sglog
from sgrequests import SgRequests
import json

def fetch_data():
    logzilla = sglog.SgLogSetup().get_logger(logger_name='pita*2')
    url = "https://pitapit.ca/wp-admin/admin-ajax.php?lang=en&action=store_search&lat="
    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36'
    }
    session = SgRequests()
    search = DynamicGeoSearch(country_codes=[SearchableCountries.CANADA])
    search.initialize()
    coord = search.next()
    identities = set()
    while coord:
        lat, long = coord
        son = session.get(url+str(lat)+"&lng="+str(long), headers = headers).json()
        result_lats = []
        result_longs = []
        result_coords = []
        topop = 0
        if len(son)!=0:
            for i in son:
                result_lats.append(i['lat'])
                result_longs.append(i['lng'])
                if i['id'] not in identities:
                    identities.add(i['id'])
                    yield i
                else:
                    topop += 1
        result_coords = list(zip(result_lats,result_longs))
        logzilla.info(f'Coordinates remaining: {search.zipcodes_remaining()}; Last request yields {len(result_coords)-topop} stores.')
        search.update_with(result_coords)
        coord = search.next()
    logzilla.info(f'Finished grabbing data!!')

def fix_hours(x):
    x = x.replace('<table role="presentation" class="wpsl-opening-hours">','')
    x = x.replace('<tr>','')
    x = x.replace('<td>','')
    x = x.replace('</td>','')
    x = x.replace('<time>',': ')
    x = x.replace('</time>',', ')
    x = x.replace('</table>','')
    x = x.replace('</tr>','')
    if len(x)<3:
        x = "<MISSING>"
    return x

def scrape():
    url="https://pitapit.ca/"
    field_defs = SimpleScraperPipeline.field_definitions(
        locator_domain = ConstantField(url),
        page_url=MappingField(mapping=['permalink'], value_transform = lambda x : x.replace('\/','/')),
        location_name=MappingField(mapping=['store'], value_transform = lambda x : x.replace('&#8211;',"-").replace('&#8217;',"'").replace('&#038;','&')),
        latitude=MappingField(mapping=['lat']),
        longitude=MappingField(mapping=['lng']),
        street_address=MultiMappingField(mapping=[['address'],['address2']], multi_mapping_concat_with = ', '),
        city=MappingField(mapping=['city']),
        state=MappingField(mapping=['state']),
        zipcode=MappingField(mapping=['zip']),
        country_code=MappingField(mapping=['country']),
        phone=MappingField(mapping=['phone']),
        store_number=MappingField(mapping=['id']),
        hours_of_operation=MappingField(mapping=['hours'], value_transform = fix_hours, is_required = False),
        location_type=MappingField(mapping=['description'], value_transform = lambda x : 'Temporarily Closed' if 'temporarily closed' in x else '<MISSING>' )
    )

    pipeline = SimpleScraperPipeline(scraper_name='pitapit.ca',
                                     data_fetcher=fetch_data,
                                     field_definitions=field_defs,
                                     log_stats_interval=15)

    pipeline.run()

if __name__ == "__main__":
    scrape()
