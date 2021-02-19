import requests_random_user_agent # ignore_check
from requests.exceptions import RequestException # ignore_check
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

logger = SgLogSetup().get_logger('napaonline_com')




show_logs = False
thread_local = threading.local()
addresses = []
base_url = "https://www.napaonline.com"


class objdict(dict):
    # wrapper class to allow accessing dict keys as object properties
    # needed in order to mock the Beautiful Soup Tag object, so we can access, for example
    # url["href"] and url.text in the code below that tests one city url
    # https://goodcode.io/articles/python-dict-object/
    def __getattr__(self, name):
        if name in self:
            return self[name]
        else:
            raise AttributeError("No such attribute: " + name)

    def __setattr__(self, name, value):
        self[name] = value

    def __delattr__(self, name):
        if name in self:
            del self[name]
        else:
            raise AttributeError("No such attribute: " + name)


def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8", newline='') as output_file:
        writer = csv.writer(output_file, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)


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
        r = thread_local.get_session().get('https://jsonip.com/')
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
        sleep()
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


def crawl_state_url(state_url):
    city_urls = []
    r = get(state_url)
    if not r:
        return city_urls
    state_soup = bs(r.text, "lxml")
    for url in state_soup.find("div", {"class": "store-browse-content"}).find_all("a"):
        city_urls.append(url)
    return city_urls


def scrape_json(data, page_url): 
    location_name = data['name']
    street_address = data['address']['streetAddress']
    city = data['address']['addressLocality']
    state = data['address']['addressRegion']
    zipp = data['address']['postalCode']
    country_code = data['address']['addressCountry']
    store_number = data['@id']
    try:
        phone = data['telephone']
    except:
        phone = "<MISSING>"
    location_type = data['@type']
    latitude = data['geo']['latitude']
    longitude = data['geo']['longitude']
    hours = ''
    for hr in data['openingHoursSpecification']:
        if hours != '': 
            hours += ', '
        hours += " " + hr['dayOfWeek'][0]
        if hr['opens'] == "00:00:00" and hr['closes'] == "00:00:00": 
            hours += " Closed"
        else:
            hours += " " + datetime.strptime(hr['opens'], "%H:%M:%S").strftime(
                "%I:%M %p") + " - " + datetime.strptime(hr['closes'], "%H:%M:%S").strftime("%I:%M %p")+" "

    store = [base_url, location_name, street_address, city, state, zipp, country_code,
                store_number, phone, location_type, latitude, longitude, hours.strip(), page_url]
    store = [str(x).encode('ascii', 'ignore').decode(
        'ascii').strip() if x else "<MISSING>" for x in store]
    return store


def scrape_store_number(soup):
    html_content = str(soup)
    match = re.search(r'\[\"entityId\"\] = \"(\d+?)\"', html_content)
    return match.group(1) if match else '<MISSING>'

def get_store_key(store): 
    # use the page_url as unique key
    return f'{store[-1]}'.lower()


def scrape_html(soup, page_url): 
    name_elem = soup.find(id="location-name")
    location_name = name_elem.text if name_elem else '<MISSING>'

    addr_elem = soup.find(itemprop="streetAddress")
    street_address = addr_elem['content'] if addr_elem else '<MISSING>'

    city_elem = soup.find(itemprop="addressLocality")
    city = city_elem['content'] if city_elem else '<MISSING>'

    state_elem = soup.find(itemprop="addressRegion")
    state = state_elem.text if state_elem else '<MISSING>'

    zipp_elem = soup.find(itemprop="postalCode")
    zipp = zipp_elem.text if zipp_elem else '<MISSING>'

    country_elem = soup.find(itemprop="addressCountry")
    country_code = country_elem.text if country_elem else '<MISSING>'

    phone_elem = soup.find(itemprop="telephone")
    phone = phone_elem.text if phone_elem else '<MISSING>'

    main_elem = soup.find(id="main")
    location_type = main_elem['itemtype'].replace('http://schema.org/', '') if main_elem else '<MISSING>'

    lat_elem = soup.find(itemprop="latitude")
    latitude = lat_elem['content'] if lat_elem else '<MISSING>'

    lng_elem = soup.find(itemprop="longitude")
    longitude = lng_elem['content'] if lng_elem else '<MISSING>'

    hours = ''
    hours_table = soup.find(class_="c-hours-details")
    if hours_table:
        hours = " ".join(list(hours_table.find('tbody').stripped_strings))
        hours = re.sub('PM ', 'PM, ', hours)

    store_number = scrape_store_number(soup)
    
    store = [base_url, location_name, street_address, city, state, zipp, country_code,
                store_number, phone, location_type, latitude, longitude, hours.strip(), page_url]
    store = [str(x).encode('ascii', 'ignore').decode(
        'ascii').strip() if x else "<MISSING>" for x in store]

    return store


def scrape_one_in_city(url):
    link_url = base_url + url['href']
    r = get(link_url)

    if not r: 
        return None

    soup = bs(r.text, "lxml")

    # make sure we're on a store detail page and not a listing page ... 
    #   we got here by looking for "(1)" in the url link, but sometimes these links are lying
    #   and we end up at a page with multiple stores instead of one
    is_detail_page = soup.find(class_="store-browse-content-listing") is None
    if not is_detail_page: 
        log(f'expected store detail page but found multiple store listings on {link_url}')
        return scrape_multiple_in_city(url)

    data = None
    try: 
        data = json.loads(soup.find(lambda tag: (
            tag.name == "script" and '"streetAddress"' in tag.text)).text)
    except: 
        log(f'>>> json data not found for {link_url} ... scraping html instead')

    if data:
        store = scrape_json(data, r.url) # use the final url as page_url in case of redirect
    else:
        store = scrape_html(soup, r.url)

    store_key = get_store_key(store)
    if store_key in addresses:
        return None
    addresses.append(store_key)
    return [store]


def scrape_multiple_in_city(url):
    stores = []
    r = get(base_url + url['href'])
    if not r: 
        return stores
    soup = bs(r.text, "lxml")
    for link in soup.find_all("div", {"class": "store-browse-store-detail"}):

        link_url = base_url + link.a['href'].replace('https://www.napaonline.com', '')
        # log(link_url)
        r = get(link_url)
        if not r: 
            continue
        soup = bs(r.text, "lxml")

        data = None
        try: 
            data = json.loads(soup.find(lambda tag: (
                tag.name == "script" and '"streetAddress"' in tag.text)).text)
        except: 
            log(f'>>> json data not found for {link_url}')
            
        if data: 
            store = scrape_json(data, r.url) # use the final url as page_url in case of redirect
        else:
            store = scrape_html(soup, r.url)

        store_key = get_store_key(store)
        if store_key in addresses:
            continue
        addresses.append(store_key)
        stores.append(store)
    return stores


def crawl_city_url(url):
    # the url argument is of type bs4.element.Tag
    # logger.info(f'type(url): {type(url)}')
    if "(1)" in url.text:
        return scrape_one_in_city(url)
    else:
        return scrape_multiple_in_city(url)


def fetch_data():

    state_urls = []
    city_urls = []
    r = get("https://www.napaonline.com/en/auto-parts-stores-near-me")

    if not r: 
        logger.info(f'could not get initial locator page. giving up')
        raise SystemExit

    soup = bs(r.text, "lxml")

    for link in soup.find("div", {"class": "store-browse-content"}).find_all("a"):
        log(base_url+link['href'])
        state_urls.append(base_url+link['href'])

    with ThreadPoolExecutor(max_workers=32) as executor:
        futures = [executor.submit(crawl_state_url, url) for url in state_urls]
         # return when all finished or after 20 min regardless
        done, not_done = wait(futures, timeout=1200, return_when=ALL_COMPLETED)
        log(f'Done futures: {len(done)}')
        log(f'Not Done futures: {len(not_done)}')

        for result in futures:
            try:
                cities_in_state = result.result()
                city_urls.extend(cities_in_state)
            except Exception as ex: 
                logger.info(f'crawl_state_url with result {result} threw exception: {ex}')
                
    log(f'found {len(city_urls)} city urls')

    with ThreadPoolExecutor(max_workers=32) as executor:
        futures = [executor.submit(crawl_city_url, url) for url in city_urls]
        for result in as_completed(futures):
            locations = result.result()
            if locations:
                for store in locations:
                    yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
