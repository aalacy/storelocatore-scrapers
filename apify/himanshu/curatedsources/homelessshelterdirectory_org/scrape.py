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

logger = SgLogSetup().get_logger('homelessshelterdirectory_org')




show_logs = False
thread_local = threading.local()
max_workers = 64
unique_locations = []
base_url = "https://www.homelessshelterdirectory.org/"


def sleep(min=0.5, max=2.5):
    duration = random.uniform(min, max)
    time.sleep(duration)


def log(*args, **kwargs):
  if (show_logs == True):
    logger.info(" ".join(map(str, args)), **kwargs)
    logger.info("")


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


def write_output(data):
    with open('data.csv', mode='w', newline='') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "updated_date", "hours_of_operation",'page_url'])
        # Body
        for row in data:
            writer.writerow(row)


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
    state_soup = bs(r.content.decode('utf-8', 'ignore'), "lxml")
    for url in state_soup.find_all("a",{"title":re.compile("homeless shelters")}):
        # log(f'city url: {url}')
        city_urls.append(url)
    return city_urls


def crawl_city_url(url):
    location_urls = []
    r = get(url['href'])
    if not r: 
        return location_urls
    soup = bs(r.content.decode('utf-8', 'ignore'), "lxml")
    for url in soup.find_all("a",{"class":"btn btn_red"}):
        page_url = url['href']
        if "homelessshelterdirectory.org" not in page_url:
            continue
        location_urls.append(page_url)
    return location_urls


def crawl_location_url(url):
    r = get(url)
    if not r: 
        return None
    location_soup = bs(r.content.decode('utf-8', 'ignore'), "lxml")
    try:
        location_name = location_soup.find("h3",{"class":"entry_title"}).text
        # remove the " - city, state" from end of location name
        location_name = " - ".join([x.strip() for x in location_name.split('-')[:-1]])
    except:
        location_name = "<MISSING>"
    
    addr = list(location_soup.find("div",{"class":"col col_6_of_12"}).find("p").stripped_strings)
    if len(addr) > 2:
        if re.sub(r'\s+',"",addr[1].replace(":","").replace("(","").replace(")","").replace("-","")).isdigit():
            street_address = "<MISSING>"
            city = city = addr[0].split(",")[0]
            state = addr[0].split(",")[1].split()[0]
            if len(addr[0].split(",")[1].split()) == 2:
                zipp = addr[0].split(",")[1].split()[1]
            else:
                zipp = "<MISSING>"
        
            phone = addr[1].replace(":","").replace("_","").replace("?","").replace(",","").replace("24hrs","").strip()
        else:

            street_address = addr[0]
            city = addr[1].split(",")[0]
            state = addr[1].split(",")[1].split()[0]
            if len(addr[1].split(",")[1].split()) == 2:
                zipp = addr[1].split(",")[1].split()[1]
            else:
                zipp = "<MISSING>"
            phone = addr[2].replace(":","").replace("_","").replace("?","").replace(",","").replace("24hrs","").strip()
    
    else:
        street_address = "<MISSING>"
        city = city = addr[0].split(",")[0]
        state = addr[0].split(",")[1].split()[0]
        if len(addr[0].split(",")[1].split()) == 2:
            zipp = addr[0].split(",")[1].split()[1]
        else:
            zipp = "<MISSING>"
    
        phone = addr[1].replace(":","").replace("_","").replace("?","").replace(",","").replace("24hrs","").strip()

    if "ext" in phone.lower():
        phone = phone.lower().split("ext")[0].strip()
    if "or" in phone:
        phone = phone.split("or")[0]
    store_number = url.split("=")[1]

    coords = location_soup.find(lambda tag:(tag.name == "script") and "setView" in tag.text).text.split("[")[1].split("]")[0]
    lat = coords.split(",")[0]
    lng = coords.split(",")[1].strip()
    if location_soup.find(lambda tag:(tag.name == "article") and "Shelter Information Last Update Date" in tag.text):
        posted_date = location_soup.find(lambda tag:(tag.name == "article") and "Shelter Information Last Update Date" in tag.text).text
        update_date = re.findall(r":\s+\d{4}-\d{2}-\d{2}",posted_date)[-1].replace(":","").strip()
    else:
        update_date = "<MISSING>"
    
    store = []
    store.append(base_url)
    store.append(location_name)
    store.append(street_address.replace("?","").strip())
    store.append(city)
    store.append(state)
    store.append(zipp)
    store.append("US")
    store.append(store_number)
    store.append(phone.replace("x305","").replace("x 203","").replace("/","").strip() if phone.replace("-","").replace("(","").replace(")","").replace(".","").replace(",","").replace("/","").strip().isdigit() and len(phone.replace("-","").replace("(","").replace(")","").replace(".","").replace(",","").replace("/","").strip()) == 10  else "<MISSING>")
    store.append("Shelter")
    store.append(lat)
    store.append(lng)
    store.append(update_date)
    store.append("<MISSING>")
    store.append(url)

    store_key = store_number + lat + '-' + lng
    if store_key in unique_locations:
        return None
    unique_locations.append(store_key)
    store = [str(x).strip() if x else "<MISSING>" for x in store]
    
    return store



def fetch_data():

    state_urls = []
    city_urls = []
    loc_urls = []

    r = get(base_url)
    if not r: 
        logger.info(f'could not get initial locator page. giving up')
        raise SystemExit

    soup = bs(r.content, "lxml")
    for s_link in soup.find_all("area",{"shape":"poly"}):
        log(s_link['href'])
        state_urls.append(s_link['href'])
    
    for url in state_urls: 
        log(url)
        
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(crawl_state_url, url) for url in state_urls]
         # return when all finished or after 20 min regardless
        done, not_done = wait(futures, timeout=1200, return_when=ALL_COMPLETED)
        log(f'Done crawl_state futures: {len(done)}')
        log(f'Not Done crawl_state futures: {len(not_done)}')
        for result in futures:
            try:
                cities_in_state = result.result()
                city_urls.extend(cities_in_state)
            except Exception as ex: 
                log(f'crawl_state_url with result {result} threw exception: {ex}')
                
    log(f'found {len(city_urls)} city urls')

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(crawl_city_url, url) for url in city_urls]
        # return when all finished or after 2 hours regardless
        done, not_done = wait(futures, timeout=7200, return_when=ALL_COMPLETED)
        log(f'Done crawl_city futures: {len(done)}')
        log(f'Not Done crawl_city futures: {len(not_done)}')
        for result in futures:
            location_urls = []
            try: 
                location_urls = result.result()
            except Exception as ex: 
                log(f'crawl_city_url with result {result} threw exception: {ex}')
            for url in location_urls: 
                if url not in loc_urls: 
                    loc_urls.append(url)

    log(f'found {len(loc_urls)} location urls')

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(crawl_location_url, url) for url in loc_urls]
        for result in as_completed(futures):
            store = None
            try: 
                store = result.result()
            except Exception as ex: 
                log(f'crawl_location_url with result {result} threw exception: {ex}')
            if store: 
                yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
