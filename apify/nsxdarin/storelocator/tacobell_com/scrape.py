import csv
from sgrequests import SgRequests
import json
import requests_random_user_agent
from requests.exceptions import RequestException
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import random
import time
import os
from datetime import datetime


show_logs = False
thread_local = threading.local()
all_location_urls = []

def sleep(min=0.5, max=2.5):
    duration = random.uniform(min, max)
    time.sleep(duration)


def log(*args, **kwargs):
  if (show_logs == True):
    print(" ".join(map(str, args)), **kwargs)
    print("")


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
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)


def get(url, attempts=1):

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

    if attempts == 10:
        print(f'could not get {url} after {attempts} tries... giving up')
        raise SystemExit

    try:
        sleep()
        session = get_session()
        log(f'getting {url}')
        r = session.get(url, headers=headers)
        r.raise_for_status()
        increment_request_count()
        return r

    except Exception as ex:
        print(f'>>> exception getting {url} on thread {threading.current_thread().ident}: {ex}')
        print(f'>>> reset session and try again')
        session = get_session(reset=True)
        return get(url, attempts+1)


def crawl_state_url(state_url):
    cities = []
    locs = []

    r2 = get(state_url)
    for line2 in r2.iter_lines():
        line2 = str(line2.decode('utf-8'))
        if '<a class="Directory-listLink" href="' in line2:
            items = line2.split('<a class="Directory-listLink" href="')
            for item in items:
                if 'data-ya-track="directory_links" data-count="(' in item:
                    curl = 'https://locations.tacobell.com/' + item.split('"')[0]
                    count = item.split('data-ya-track="directory_links" data-count="(')[1].split(')')[0]
                    if count == '1':
                        if curl not in all_location_urls:
                            all_location_urls.append(curl)
                            locs.append(curl)
                    else:
                        cities.append(curl)

    results = {
        'city_urls': cities,
        'loc_urls': locs
    }
    return results


def crawl_city_url(city_url):
    locs = []

    r3 = get(city_url)
    for line3 in r3.iter_lines():
        line3 = str(line3.decode('utf-8'))
        if '<a data-ya-track="visit_site" href="../' in line3:
            items = line3.split('<a data-ya-track="visit_site" href="../')
            for item in items:
                if 'View Page' in item:
                    lurl = 'https://locations.tacobell.com/' + item.split('"')[0]
                    if lurl not in all_location_urls:
                        all_location_urls.append(lurl)
                        locs.append(lurl)
    return locs


def crawl_location_url(loc_url): 

    website = 'tacobell.com'
    typ = 'Restaurant'
    name = ''
    add = ''
    city = ''
    state = ''
    zc = ''
    country = 'US'
    store = ''
    phone = ''
    hours = ''
    lat = ''
    lng = ''
    r4 = get(loc_url)
    for line4 in r4.iter_lines():
        line4 = str(line4.decode('utf-8'))
        if '"c_siteNumber":"' in line4 and store == '':
            store = line4.split('"c_siteNumber":"')[1].split('"')[0]
        if 'property="og:title" content="' in line4:
            name = line4.split('property="og:title" content="')[1].split(' |')[0]
            add = line4.split('<span class="c-address-street-1">')[1].split('<')[0].strip()
            city = line4.split('<span class="c-address-city">')[1].split('<')[0]
            state = line4.split('itemprop="addressRegion">')[1].split('<')[0]
            zc = line4.split('itemprop="postalCode">')[1].split('<')[0].strip()
            phone = line4.split('itemprop="telephone" id="phone-main">')[1].split('<')[0]
            lat = line4.split('<meta itemprop="latitude" content="')[1].split('"')[0]
            lng = line4.split('<meta itemprop="longitude" content="')[1].split('"')[0]
            try:
                hrs = line4.split('Drive-Thru Hours</h4>')[1].split("}]' data-")[0]
                days = hrs.split('"day":"')
                for day in days:
                    if '"intervals":' in day:
                        if hours == '':
                            try:
                                hours = day.split('"')[0] + ': ' + day.split('"start":')[1].split('}')[0] + '-' + day.split('"end":')[1].split(',')[0]
                            except:
                                pass
                        else:
                            try:
                                hours = hours + '; ' + day.split('"')[0] + ': ' + day.split('"start":')[1].split('}')[0] + '-' + day.split('"end":')[1].split(',')[0]
                            except:
                                pass
            except:
                pass
    if hours == '':
        hours = '<MISSING>'
    if lat == '':
        lat = '<MISSING>'
    if lng == '':
        lng = '<MISSING>'
    if name != '':
        if store == '':
            store = '<MISSING>'
        return [website, loc_url, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

    return None


def fetch_data():

    locs = []
    state_urls = []

    url = 'https://locations.tacobell.com/'
    r = get(url)
    for line in r.iter_lines():
        line = str(line.decode('utf-8'))
        if '<span class="Directory-listLinkText">' in line:
            items = line.split('<span class="Directory-listLinkText">')
            for item in items:
                if '"Directory-listLink" href="' in item:
                    surl = 'https://locations.tacobell.com/' + item.split('"Directory-listLink" href="')[1].split('"')[0]
                    log(surl)
                    state_urls.append(surl)

    city_urls = []
    location_urls = []

    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = [executor.submit(crawl_state_url, url) for url in state_urls]
        for result in as_completed(futures):
            d = result.result()
            city_urls.extend(d['city_urls'])
            location_urls.extend(d['loc_urls'])


    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = [executor.submit(crawl_city_url, url) for url in city_urls]
        for result in as_completed(futures):
            location_urls.extend(result.result())

    
    log(f'>>>>>>> found {len(location_urls)} location urls <<<<<<<')
    
    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = [executor.submit(crawl_location_url, url) for url in location_urls]
        for result in as_completed(futures):
            location = result.result()
            if location:
                yield location
    
            

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
