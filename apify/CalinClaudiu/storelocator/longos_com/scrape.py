from sgscrape.simple_scraper_pipeline import *
from sgscrape import simple_network_utils as net_utils
from sgscrape import simple_utils as utils
from sglogging import sglog
from sgrequests import SgRequests
from bs4 import BeautifulSoup
from sgselenium import SgChrome, SgSelenium
import time
import itertools

def para(url):
    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36'
    }
    session = SgRequests()
    son = session.get(url,headers=headers).json()
    return son

def fetch_data():
    logzilla = sglog.SgLogSetup().get_logger(logger_name='Scraper')
    url = "https://www.longos.com/stores/"
    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36'
    }
    links = []
    with SgChrome() as driver:
        logzilla.info(f'Opening {url}')
        driver.get(url)
        logzilla.info(f'Waiting for requests to load')
        time.sleep(5)
        soup = BeautifulSoup(driver.page_source, 'lxml')
        for i in soup.find_all('link',{'href':lambda x : x and x.startswith('/page-data/store/')}):
            links.append('https://www.longos.com'+i['href'])
    j = utils.parallelize(
                search_space = links,
                fetch_results_for_rec = para,
                max_threads = 10,
                print_stats_interval = 10
                )
    for i in j:
        yield i['result']['pageContext']['store']
    logzilla.info(f'Finished grabbing data!!')

def nice_hours(x):
    days = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
    x = x.split("'day'")
    x.pop(0)
    parsed = []
    for i in x:
        try:
            i = i.split(',')
            parsed.append(str(i[1].split(':')[-1]+' - '+i[2].split(':')[-1]).replace('000','0:00').replace('00',':00').replace('::',':'))
        except:
            continue
    hours = [[i]for i in itertools.zip_longest(days, parsed, fillvalue='Closed')]
    x = []
    for i in hours:
        x.append(': '.join(str(j) for j in i[0]))

    return '; '.join(x).replace('}','').replace(']','')

def scrape():
    url="https://www.longos.com"
    field_defs = SimpleScraperPipeline.field_definitions(
        locator_domain = ConstantField(url),
        page_url=MappingField(mapping=['alias'], value_transform = lambda x : url+x+'/'),
        location_name=MappingField(mapping=['name']),
        latitude=MappingField(mapping=['latitude']),
        longitude=MappingField(mapping=['longitude']),
        street_address=MappingField(mapping=['address1']),
        city=MappingField(mapping=['city']),
        state=MappingField(mapping=['province']),
        zipcode=MappingField(mapping=['postalCode']),
        country_code=MappingField(mapping=['field_store_address','country_code']),
        phone=MappingField(mapping=['phone']),
        store_number=MappingField(mapping=['id']),
        hours_of_operation=MappingField(mapping=['storeHours'], value_transform = nice_hours),
        location_type=MissingField()
    )

    pipeline = SimpleScraperPipeline(scraper_name='longos.com',
                                     data_fetcher=fetch_data,
                                     field_definitions=field_defs,
                                     log_stats_interval=25)

    pipeline.run()

if __name__ == "__main__":
    scrape()
