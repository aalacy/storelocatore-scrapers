# coding=UTF-8
import csv
from bs4 import BeautifulSoup
import json
import time
import random
from sgrequests import SgRequests
from requests.exceptions import ProxyError
import requests_random_user_agent
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import html
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('comerica_com')




show_logs = False


thread_local = threading.local()


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


def get_session(reset=False):
  # give each thread its own session object.
  # when using proxy, each thread's session will have a unique IP, and we'll switch IPs every 10 requests
  if (not hasattr(thread_local, "session")) or (hasattr(thread_local, "request_count") and thread_local.request_count == 10) or (reset == True):
    thread_local.session = SgRequests()
    reset_request_count()
    # print out what the new IP is ...
    if show_logs == True:
        r = thread_local.session.get('https://jsonip.com/')
        log(f"new IP for thread id {threading.current_thread().ident}: {r.json()['ip']}")

  return thread_local.session


def reset_request_count():
  if hasattr(thread_local, "request_count"):
    thread_local.request_count = 0


def increment_request_count():
  if not hasattr(thread_local, "request_count"):
    thread_local.request_count = 1
  else:
    thread_local.request_count += 1


def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8", newline="") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def get(url): 

    r = None
    headers = {
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-User': '?1',
        'Sec-Fetch-Dest': 'document',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9,la;q=0.8'
    }

    try:
        sleep()
        session = get_session()

        session.get_session().cookies.clear()
        r = session.get(url, headers=headers)
        r.raise_for_status()
        
        log(url)
        increment_request_count()

    except (ProxyError, OSError) as err:
        # attempt to handle errors such as "cannot connect to proxy, timed out"
        log('*************** proxy error ***************')
        log(f'url: {url}')
        log(err)
        log('************ resetting session ************')
        session = get_session(reset=True)
        # try this request again
        return get(url)

    return r


def get_location_detail(url): 
    r = get(url)

    soup = BeautifulSoup(r.text, "lxml")
    script_tag = soup.find(lambda tag: (tag.name == "script") and "var loc" in tag.text)
    
    # parse the json string from the javascript 
    data_str = script_tag.string.split('var loc = ')[1].split('var map;')[0].replace("};", "}")

    data = json.loads(data_str)

    street_address = (data['street'] + " " + str(data['additional'])).replace("None", "").strip()
    city = data['city']
    state = data['province']
    zipp = data['postal_code']
    country_code = data['country']
    store_number = data['id']
    
    location_type = "/".join(data['m_entity_types'])
    if location_type in ["atm", "atm/itm"]:
        # skip this atm-only location
        return None

    latitude = data['lat']
    longitude = data['lng']

    # default values for items pulled from the branch data
    location_name = '<MISSING>'
    phone = '<MISSING>'
    hours_of_operation = '<MISSING>'

    branch = find_location_entity_by_type(data, 'branch')

    if not branch: 
        # some locations are type "tls", such as https://locations.comerica.com/location/tls-headquarters-palo-alto
        branch = find_location_entity_by_type(data, 'tls')

    if branch: 
        location_name = html.unescape(branch['name'])

        if branch['phone'] != "":
            phone = branch['phone']

        hours = get_hours(branch)
        if hours:
            hours_of_operation = hours

    location = {
        'locator_domain': "https://www.comerica.com",
        'location_name': location_name,
        'street_address': street_address,
        'city': city,
        'state': state,
        'zip': zipp,
        'country_code': country_code,
        'store_number': store_number,
        'phone': phone,
        'location_type': location_type,
        'latitude': latitude,
        'longitude': longitude,
        'hours_of_operation': hours_of_operation,
        'page_url': url
    }

    return list(location.values())


def find_location_entity_by_type(data, type): 
    # find the item in the entities dict that has type equal to the type argument
    return next((item for item in data['entities'] if item['type'] == type), None)


def get_hours(branch): 
    hours_entries = None
    hours_of_operation = None

    if 'lobby' in branch['open_hours_formatted']:
        # walk-in location (may also have drive-through, but we'll use lobby hours)
        hours_entries = branch['open_hours_formatted']['lobby']
    elif 'drive' in branch['open_hours_formatted']:
        # drive-through only location
        hours_entries = branch['open_hours_formatted']['drive']

    if hours_entries:
        hours_of_operation = format_hours(hours_entries)
    
    return hours_of_operation


def format_hours(hours):
    # the hours argument here is from the json data.
    # it's a list of 7 strings corresponding with days in this order:
    days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    
    formatted = [
        f'{day}: {"Closed" if hours[idx] is None else hours[idx]}' for idx, day in enumerate(days)]
    
    return ', '.join(formatted)


def fetch_data():
    
    r = get('https://locations.comerica.com/sitemap.xml')
    soup = BeautifulSoup(r.text, "lxml")
    locs = soup.select('urlset url:not(:first-child) loc')

    loc_urls = [tag.text for tag in locs if 'location/atm-' not in tag.text]
    log(f'total locations (without ATMs): {len(loc_urls)}')

         
    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = [executor.submit(get_location_detail, url) for url in loc_urls]
        for result in as_completed(futures):
            location = result.result()
            if location:
                yield location


def scrape():
    data = fetch_data()
    write_output(data)


log(f'start time: {get_time()}')
scrape()
log(f'end time: {get_time()}')
