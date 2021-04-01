import requests_random_user_agent # ignore_check
from requests.exceptions import RequestException, SSLError, ProxyError # ignore_check
from concurrent.futures import ThreadPoolExecutor, as_completed, wait, ALL_COMPLETED
import threading
import random
import time
import os
import csv
import re
from bs4 import BeautifulSoup as bs
import json
from datetime import datetime
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('kroger_com__fuel')


def override_retries():
    # monkey patch sgrequests in order to set max retries
    import requests  # ignore_check

    def new_init(self): 
        requests.packages.urllib3.disable_warnings()
        self.session = self.requests_retry_session(retries=0)

    SgRequests.__init__ = new_init


def override_sgrequests_get():
    # monkey patch sgrequests in order to allow shorter timeout
    def new_get(self, url, **kwargs):
        kwargs.update({'verify': False})
        # kwargs.update({'timeout': (100, 100)})
        return self.session.get(url, **kwargs)

    SgRequests.get = new_get


override_retries()
override_sgrequests_get()

# regex pattern to get the json data from each page
re_page_data = re.compile("INITIAL_STATE__ = JSON\.parse\('(.+?)'\)")

show_logs = False
thread_local = threading.local()
thread_ips = {}
banned_ips = set()


def get_time():
    t = time.localtime()
    return time.strftime("%H:%M:%S", t)


def sleep(min=0.5, max=2.5):
    duration = random.uniform(min, max)
    time.sleep(duration)


def log(*args, **kwargs):
    if (show_logs == True):
        logger.info(" ".join(map(str, args)), **kwargs)
        logger.info("")


def get_time():
    t = time.localtime()
    return time.strftime("%H:%M:%S", t)


def get_session_with_unbanned_ip():
    # creates new session on the current thread
    # checks whether ip was already banned 
    # loops until it finds ip not already banned
    # returns the new ip address
    attempts = 0
    max_attempts = 40
    new_ip = None
    while attempts <= max_attempts:
        attempts += 1
        log(f">>> attempt {attempts} getting new IP for thread id {threading.current_thread().ident}")
        thread_local.session = SgRequests()
        try:
            r = thread_local.session.get('https://jsonip.com/')
        except (RequestException, SSLError, ProxyError, OSError, Exception) as err:
            log(f'>>> error checking ip address on thread  {threading.current_thread().ident}')
            continue
        new_ip = r.json()['ip']
        log(f">>> new IP for thread id {threading.current_thread().ident}: {new_ip}")
        if new_ip in banned_ips:
            log(f'>>> IP {new_ip} on thread {threading.current_thread().ident} already banned')
            log(f'>>> Banned IPs ({len(banned_ips)})', banned_ips)
        else:
            thread_ips[threading.current_thread().ident] = new_ip
            break
    if not new_ip:
        logger.info(f'Could not get an unbanned IP from proxy after {max_attempts} tries.')
    return new_ip


def get_session(reset=False):
    # give each thread its own session object.
    # when using proxy, each thread's session will have a unique IP
    if (not hasattr(thread_local, "session")) or (reset == True):
        
        reset_request_count()
        new_ip = get_session_with_unbanned_ip()
        if not new_ip: 
            raise SystemExit('Proxy not giving us any new, unbanned IPs.')
        thread_ips[threading.current_thread().ident] = new_ip
        
    return thread_local.session


def reset_request_count():
    if hasattr(thread_local, "request_count"):
        thread_local.request_count = 0


def increment_request_count():
    if not hasattr(thread_local, "request_count"):
        thread_local.request_count = 1
    else:
        thread_local.request_count += 1


def get(url, attempt=1):

    if attempt == 41:
        log(f'***** cannot get {url} on thread {threading.current_thread().ident} after {attempt-1} tries. giving up *****')
        return None

    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'cache-control': 'max-age=0',
        # 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36',
        # the `requests_random_user_agent` package automatically rotates user-agent strings
    }

    try:
        sleep()
        session = get_session()
        # session.get_session().cookies.clear()
        # log(f'getting {url}')
        # need override_sgrequests_get() in order to honor the timeout passed in below
        r = session.get(url, headers=headers, timeout=10, verify=False) 
        log(f'--- status for {url} on thread {threading.current_thread().ident} >>> ', r.status_code)
        r.raise_for_status()
        increment_request_count()
        return r

    except (RequestException, SSLError, ProxyError, OSError, Exception) as err:
        # if hasattr(err, 'response') and err.response is not None and err.response.status_code == 404:
        status_code = get_status_from_err(err)

        if status_code == 404:
            log(f'Got 404 getting {url}')
            return None
        
        if status_code == 403:
            log(f'Got 403 getting {url}. Adding IP {thread_ips[threading.current_thread().ident]} to banned list.')
            banned_ips.add(thread_ips[threading.current_thread().ident])

        # attempt to handle 403 forbidden and other errors such as "cannot connect to proxy, timed out, etc"
        err_msg = f'***** error getting {url} on thread {threading.current_thread().ident}: {err} \n - resetting session ******'
        log(err_msg)
        session = get_session(reset=True)
        # try this request again
        return get(url, attempt=attempt+1)


def get_status_from_err(err):
    if hasattr(err, 'response') and err.response is not None and hasattr(err.response, 'status_code'):
        return err.response.status_code
    return None


def write_output(data):
    with open('data.csv', mode='w', newline='') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def scrape_location(url):
    base_url = 'https://www.kroger.com/'
    try:
        page_url = url.text
        r = get(page_url)

        if not r: 
            log(f'::::: Could not get source of location {url}. Returning None.')
            log('----------')
            return None

        match = re.search(re_page_data, r.text)
        data_string = match.group(1)

        # fix up the string so json can parse it without errors
        data_string = data_string.replace('\\', '\\\\')
        data_string = re.sub('(\"contentHash\":\")(W/.*?\")(\"})', '\\1\\3', data_string) 
        
        page_data = json.loads(data_string)

        data = page_data["storeDetails"]["store"] if "store" in page_data["storeDetails"] else None
        if not data: 
            log('::::: no store data here')
            log('----------')
            return None

        has_fuel = next((item for item in data["departments"] if item["friendlyName"] == "Gas Station"), None)

        if not has_fuel: 
            log('::::: no fuel here')
            log('----------')
            return None
        
        location_name = f"{data['vanityName']} {data['bannerDisplayName']}"
        street_address = data['address']['addressLine1']
        city = data['address']['city']
        state = data['address']['stateCode']
        zipp = data['address']['zip']
        country_code = "US"
        store_number = data['storeNumber']
        phone = data['phoneNumber']
        location_type = data['banner'] # use the branding as loc type
        lat = data['latitude']
        lng = data['longitude']
        hours = ", ".join([f"{item['displayName']}: {item['displayHours']}" for item in data['formattedHours']])

        store = []
        store.append(base_url)
        store.append(location_name)
        store.append(street_address)
        store.append(city)
        store.append(state)
        store.append(zipp)   
        store.append(country_code)
        store.append(store_number)
        store.append(phone)
        store.append(location_type)
        store.append(lat)
        store.append(lng)
        store.append(hours)
        store.append(page_url)     
    
        store = [str(x).strip() if x else "<MISSING>" for x in store]
        log(store)
        log('----------')
        return store
    
    except Exception as ex:
        logger.info(f'Error at {url}: {ex}')
        return None


def get_sitemap_urls():
    r = get("https://www.kroger.com/storelocator-sitemap.xml")
    if not r:
        raise SystemExit('Could not get sitemap.')
    soup = bs(r.text,"lxml")
    return soup.find_all("loc")[:-1]
    

def fetch_data():
    
    location_urls = get_sitemap_urls()
    log(f'found {len(location_urls)} location urls')
    
    # scrape all locations
    unique_locs = []
    with ThreadPoolExecutor(max_workers=16) as executor:
        futures = [executor.submit(scrape_location, url) for url in location_urls] 
        for result in as_completed(futures):
            try: 
                store = result.result()
                if store:
                    store_key = store[-1]
                    if store_key not in unique_locs:
                        unique_locs.append(store_key)
                        yield store
            except Exception as ex: 
                logger.info(f'>>> exception getting result from scrape_usa_location future: {ex}')
        
        
   
def scrape():
    data = fetch_data()
    write_output(data)

log(f'Starting at: {get_time()}')
scrape()
log(f'Finished at: {get_time()}')
