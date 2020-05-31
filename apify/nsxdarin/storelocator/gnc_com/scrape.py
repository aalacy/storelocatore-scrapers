import csv
from sgrequests import SgRequests
import json
import re
import time
import random
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from requests.exceptions import ProxyError


show_logs = False

thread_local = threading.local()

post_headers = {
  'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
  'accept-encoding': 'gzip, deflate, br',
  'accept-language': 'en-US,en;q=0.9,la;q=0.8',
  'cache-control': 'max-age=0',
  'origin': 'https://www.gnc.com',
  'referer': 'https://www.gnc.com/on/demandware.store/Sites-GNC2-Site/default/Stores-FindStores',
  'sec-fetch-dest': 'document',
  'sec-fetch-mode': 'navigate',
  'sec-fetch-site': 'same-origin',
  'sec-fetch-user': '?1',
  'upgrade-insecure-requests': '1',
  'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
  'content-type': 'application/x-www-form-urlencoded' 
}
get_headers = {
  'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
  'accept-encoding': 'gzip, deflate, br',
  'accept-language': 'en-US,en;q=0.9,la;q=0.8',
  'sec-fetch-dest': 'document',
  'sec-fetch-mode': 'navigate',
  'sec-fetch-site': 'none',
  'upgrade-insecure-requests': '1',
  'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
}

re_get_json = re.compile('map\.data\.addGeoJson\(\s*JSON\.parse\(\s*eqfeed_callback\((.+?)\)\s*\)\s*\);')
re_get_phone = re.compile('<a href="tel:(.+?)" class="store-phone">')
re_get_hours_section = re.compile('<div class="storeLocatorHours">(.+?)</div>')
re_get_hours_days = re.compile('<span><span>(.+?)</span>(.+?)</span>')


def sleep(min=1, max=3):
    duration = random.randint(min, max)
    # log('sleeping ', duration)
    time.sleep(duration)


def log(*args, **kwargs):
  if (show_logs == True):
    print(" ".join(map(str, args)), **kwargs)


def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)


def get_session():
  # give each thread its own session object.
  # when using proxy, each thread's session will have a unique IP, and we'll switch IPs every 10 requests
  if (not hasattr(thread_local, "session")) or (hasattr(thread_local, "request_count") and thread_local.request_count == 10):
    thread_local.session = SgRequests()
    # print out what the new IP is ...
    if show_logs == True:
        r = thread_local.session.get('https://jsonip.com/')
        log(f"new IP for thread id {threading.current_thread().ident}: {r.json()['ip']}")
    
  if hasattr(thread_local, "request_count") and thread_local.request_count == 10:
    reset_request_count()

  return thread_local.session


def reset_request_count():
  if hasattr(thread_local, "request_count"):
    thread_local.request_count = 0


def increment_request_count():
  if not hasattr(thread_local, "request_count"):
    thread_local.request_count = 1
  else:
    thread_local.request_count += 1


def get_json_data(html): 
    match = re.search(re_get_json, html)
    json_text = match.group(1)
    return json.loads(json_text)


def get_phone(html): 
    match = re.search(re_get_phone, html)
    if match is None: 
        return '<MISSING>'
    else:
        return match.group(1)


def get_hours(html): 
    match_section = re.search(re_get_hours_section, html)
    if match_section is None: 
        return '<MISSING>'

    hours = ''
    match_days = re.findall(re_get_hours_days, match_section.group(1))
    if len(match_days) == 0:
        return '<MISSING>'

    for m in match_days: 
        if len(hours) > 0: 
            hours = hours + ', '
        hours = f'{hours} {m[0]}: {m[1]}'

    return hours


def search_zip(zip): 
    log('searching: ', zip)
    url = 'https://www.gnc.com/on/demandware.store/Sites-GNC2-Site/default/Stores-FindStores'
    payload = {'dwfrm_storelocator_countryCode': 'US',
                'dwfrm_storelocator_distanceUnit': 'mi',
                'dwfrm_storelocator_postalCode': zip,
                'dwfrm_storelocator_maxdistance': '500',
                'dwfrm_storelocator_findbyzip': 'Search'}
    session = get_session()
    sleep()
    r = session.post(url, headers=post_headers, data=payload)
    r.raise_for_status()
    increment_request_count()
    return get_json_data(r.text)["features"]


def get_location(loc):
    props = loc["properties"]
    store_id = props["storenumber"]
    website = 'gnc.com'
    typ = '<MISSING>'
    name = props["title"]
    url = 'https://www.gnc.com/store-details?StoreID=' + store_id
    addr = props['address1']
    if props['address2'] is not None:
        addr = addr + ', ' + props['address2']
    city = props['city']
    state = props['state']
    zc = props['postalCode']
    lat = loc["geometry"]["coordinates"][1]
    lng = loc["geometry"]["coordinates"][0]
    country = 'US'

    session = get_session()
    sleep()

    try: 
        r = session.get(url, headers=get_headers)
        r.raise_for_status()
    except ProxyError as proxy_err:
        # attempt to handle "cannot connect to proxy, timed out"
        log(f'ProxyError: {proxy_err}')
        log('resetting session')
        session = get_session()
        r = session.get(url, headers=get_headers)
        r.raise_for_status()

    increment_request_count()
    log(f'Pulling Store {url}')
    phone = get_phone(r.text)
    hours = get_hours(r.text)

    return [website, url, name, addr, city, state, zc, country, store_id, phone, typ, lat, lng, hours]


def fetch_data():
    store_ids = []
    zips = ['60007','10002','90210','96795','99515','98115','88901','87101','59715','80014','75001','32034','70032','37011','63101','58102','55408']
    search_results = []

    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = [executor.submit(search_zip, zipcode) for zipcode in zips]
        for result in as_completed(futures):
            locations = result.result()
            for loc in locations: 
                store_id = loc['properties']['storenumber']
                if store_id not in store_ids:
                    log(f'queuing store id: {store_id}')
                    search_results.append(loc)
                    store_ids.append(store_id)

    log(f'found {len(search_results)} locations')

    with ThreadPoolExecutor(max_workers=8) as executor: 
        futures = [executor.submit(get_location, result) for result in search_results]
        for result in as_completed(futures):
            loc = result.result()
            if loc is not None:
                yield loc
            

def scrape():
    data = fetch_data()
    write_output(data)


scrape()
