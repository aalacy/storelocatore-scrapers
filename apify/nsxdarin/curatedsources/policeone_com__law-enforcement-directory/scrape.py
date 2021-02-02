import requests_random_user_agent # ignore_check
from requests.exceptions import RequestException # ignore_check
from concurrent.futures import ThreadPoolExecutor, as_completed, wait, ALL_COMPLETED
import threading
import random
import time
import os
import csv
import re
import json
from datetime import datetime
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('policeone_com__law-enforcement-directory')




show_logs = False
thread_local = threading.local()
unique_addresses = []



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
        log(
            f"new IP for thread id {threading.current_thread().ident}: {r.json()['ip']}")

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

    if attempt == 5:
        log(f'***** cannot get {url} on thread {threading.current_thread().ident} after {attempt} tries. giving up *****')
        return None

    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9,la;q=0.8',
        'Connection': 'keep-alive',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1'
        # the `requests_random_user_agent` package automatically rotates user-agent strings
        # 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
    }

    try:
        # sleep()
        session = get_session()
        session.get_session().cookies.clear()
        log(f'getting {url}')
        r = session.get(url, headers=headers, timeout=15)
        log(f'status for {url} >>> ', r.status_code)
        r.raise_for_status()
        increment_request_count()
        return r

    except (RequestException, OSError) as err:
        if err.response is not None and err.response.status_code == 404:
            log(f'Got 404 getting {url}')
            return None

        # attempt to handle 403 forbidden and other errors such as "cannot connect to proxy, timed out, etc"
        log(f'***** error getting {url} on thread {threading.current_thread().ident}')
        log(err)
        log('****** resetting session')
        session = get_session(reset=True)
        # try this request again
        return get(url, attempt=attempt+1)


def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)


def scrape_search_pages():
    alllocs = []
    page = 0
    Found = True
    while Found:
        Found = False
        page = page + 1
        log('Page: ' + str(page))
        url = 'https://www.policeone.com/law-enforcement-directory/search/page-' + str(page)
        r = get(url)
        if r is None: 
            Found = False
            continue
        if r.status_code != 200: 
            log(f'got status {r.status_code} for {url}')
        for line in r.iter_lines():
            line = str(line.decode('utf-8'))
            if '<a class="Table-row " data-js-hover href="' in line:
                Found = True
                lurl = 'https://www.policeone.com' + line.split('href="')[1].split('"')[0]
                if lurl not in alllocs:
                    alllocs.append(lurl)
                    log(f'total locations found: {len(alllocs)}')
    return alllocs


def scrape_loc_url(loc): 
    log(loc)
    r = get(loc)
    if (r.status_code != 200): 
        log(f'got status {r.status_code} for {loc}')
        return None
    country = 'US'
    website = 'policeone.com/law-enforcement-directory'
    name = ''
    add = ''
    city = ''
    state = ''
    zc = ''
    store = '<MISSING>'
    phone = ''
    lat = '<MISSING>'
    lng = '<MISSING>'
    hours = '<MISSING>'
    lines = r.iter_lines()
    for line in lines:
        line = str(line.decode('utf-8'))
        if '<title>' in line:
            name = line.split('<title>')[1].split('<')[0]
        if 'Country:</dt>' in line:
            g = next(lines)
            g = str(g.decode('utf-8'))
            country = g.split('>')[1].split('<')[0]
            if 'States' in country:
                country = 'US'
            if 'Canada' in country:
                country = 'CA'
        if 'Address 1:</dt>' in line:
            g = next(lines)
            g = str(g.decode('utf-8'))
            add = g.split('>')[1].split('<')[0]
        if 'Address 2:</dt>' in line:
            g = next(lines)
            g = str(g.decode('utf-8'))
            add = add + ' ' + g.split('>')[1].split('<')[0]
        if 'City:</dt>' in line:
            g = next(lines)
            g = str(g.decode('utf-8'))
            city = g.split('>')[1].split('<')[0]
        if 'State:</dt>' in line:
            g = next(lines)
            g = str(g.decode('utf-8'))
            state = g.split('>')[1].split('<')[0]
        if 'Zip Code:</dt>' in line:
            g = next(lines)
            g = str(g.decode('utf-8'))
            zc = g.split('>')[1].split('<')[0]
        if 'Phone #:</dt>' in line:
            g = next(lines)
            g = str(g.decode('utf-8'))
            phone = g.split('>')[1].split('<')[0]
        if 'Type:</dt>' in line:
            g = next(lines)
            g = str(g.decode('utf-8'))
            typ = g.split('>')[1].split('<')[0]
    store = [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]
    log(store, '\n')
    return store


def fetch_data():
    location_urls = scrape_search_pages()
    log(f'found {len(location_urls)} unique locations')

    with ThreadPoolExecutor(max_workers=32) as executor:
        futures = [executor.submit(scrape_loc_url, url) for url in location_urls]
        for result in as_completed(futures):
            store = None
            try:            
                store = result.result()
            except Exception as ex: 
                log(f'scrape_loc_url with result {result} threw exception: {ex}')
            if store:
                key = store[1] #url as key
                if key not in unique_addresses:
                    unique_addresses.append(key)
                    yield store
            

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
