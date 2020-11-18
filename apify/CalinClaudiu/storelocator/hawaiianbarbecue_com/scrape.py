from sgscrape.simple_scraper_pipeline import *
from sgscrape import simple_network_utils as net_utils
from sgscrape import simple_utils as utils
from sglogging import sglog
from sgrequests import SgRequests


def fetch_data():
    logzilla = sglog.SgLogSetup().get_logger(logger_name='Scraper')
    url = "https://www.hawaiianbarbecue.com/wp-json/wp/v2/locations?page="
    ex = "&per_page=100"
    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36'
    }
    session = SgRequests()
    k = 1
    page = 1
    while k == 1:   
        son = session.get(url+str(page)+ex, headers = headers).json()
        if(len(son))==3:
            try:
                k = son['data']['status']
            except:
                pass
        if k == 1:
            for i in son:
                yield i
        page += 1
    
    logzilla.info(f'Finished grabbing data!!')

def nice_hours(x):
    x = str(x)
    x = x.replace('None','<MISSING>').replace('<p>','').replace('</p>','.').replace('<br />','; ').replace('\n','').replace("', '",'; ').replace("': '",': ').replace("'",'').replace('}','').replace('{','')
    return x

def good_addr(x):
    h=[]
    try:
        x = x.split(',')
    except:
        pass
    for i in x:
        if 'Click' not in i and 'To-Go' not in i:
            h.append(i)
    h = ', '.join(h)
    h = h.replace('<br \/>',' ').replace('<br>',' ').replace('<BR>',' ')
    return h
def scrape():
    url="https://www.hawaiianbarbecue.com/"
    field_defs = SimpleScraperPipeline.field_definitions(
        locator_domain = ConstantField(url),
        page_url=MappingField(mapping=['link']),
        location_name=MappingField(mapping=['acf','restaurant_name'], is_required = False),
        latitude=MappingField(mapping=['acf','location','lat']),
        longitude=MappingField(mapping=['acf','location','lng']),
        street_address=MultiMappingField(mapping=[['acf','street_line_1'],['acf','street_line_2']], multi_mapping_concat_with = ', ', value_transform = good_addr),
        city=MappingField(mapping=['acf','city']),
        state=MappingField(mapping=['acf','state']),
        zipcode=MappingField(mapping=['acf','zip_code']),
        country_code=MappingField(mapping=['acf','country'], is_required = False),
        phone=MappingField(mapping=['acf','phone'], is_required = False),
        store_number=MappingField(mapping=['id']),
        hours_of_operation=MappingField(mapping=['acf','hours'], is_required = False, value_transform = nice_hours),
        location_type=MappingField(mapping=['type'])
    )

    pipeline = SimpleScraperPipeline(scraper_name='hawaiianbarbecue.com',
                                     data_fetcher=fetch_data,
                                     field_definitions=field_defs,
                                     log_stats_interval=25)

    pipeline.run()

if __name__ == "__main__":
    scrape()
