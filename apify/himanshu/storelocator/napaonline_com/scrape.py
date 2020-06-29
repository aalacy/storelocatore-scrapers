import requests_random_user_agent
from requests.exceptions import RequestException
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import random
import time
import os
import csv
from bs4 import BeautifulSoup as bs
import json
from datetime import datetime
from sgrequests import SgRequests


show_logs = False
thread_local = threading.local()
addresses = []
base_url = "https://www.napaonline.com"


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
    print(" ".join(map(str, args)), **kwargs)
    print("")


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


def get(url):

    r = None
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

        session.session.cookies.clear()
        log(f'getting {url}')
        r = session.get(url, headers=headers)
        r.raise_for_status()

        increment_request_count()

    except (RequestException, OSError) as err:
        # attempt to handle 403 forbidden and other errors such as "cannot connect to proxy, timed out, etc"
        log(f'***** error getting {url} on thread {threading.current_thread().ident}')
        log(err)
        log('****** resetting session')
        session = get_session(reset=True)
        # try this request again
        return get(url)

    return r


def crawl_state_url(state_url):
    city_urls = []
    state_soup = bs(get(state_url).text, "lxml")
    for url in state_soup.find("div", {"class": "store-browse-content"}).find_all("a"):
        city_urls.append(url)
    return city_urls


def scrape_one_in_city(url):
    page_url = get(base_url+url['href']).url
    # log(page_url)
    location_soup = bs(get(page_url).text, "lxml")

    data = json.loads(location_soup.find(lambda tag: (
        tag.name == "script" and '"streetAddress"' in tag.text)).text)
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
        hours += " " + hr['dayOfWeek'][0] + " " + datetime.strptime(hr['opens'], "%H:%M:%S").strftime(
            "%I:%M %p") + " - "+datetime.strptime(hr['closes'], "%H:%M:%S").strftime("%I:%M %p")+" "

    store = [base_url, location_name, street_address, city, state, zipp, country_code,
             store_number, phone, location_type, latitude, longitude, hours.strip(), page_url]
    store = [str(x).encode('ascii', 'ignore').decode(
        'ascii').strip() if x else "<MISSING>" for x in store]
    if store[2] in addresses:
        return None
    addresses.append(store[2])
    return [store]


def scrape_multiple_in_city(url):
    stores = []
    soup = bs(get(base_url + url['href']).text, "lxml")
    for link in soup.find_all("div", {"class": "store-browse-store-detail"}):

        page_url = base_url + link.a['href']
        # log(page_url)
        location_soup = bs(get(page_url).text, "lxml")

        data = json.loads(location_soup.find(lambda tag: (
            tag.name == "script" and '"streetAddress"' in tag.text)).text)
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
            hours += " " + hr['dayOfWeek'][0] + " " + datetime.strptime(hr['opens'], "%H:%M:%S").strftime(
                "%I:%M %p") + " - " + datetime.strptime(hr['closes'], "%H:%M:%S").strftime("%I:%M %p")+" "

        store = [base_url, location_name, street_address, city, state, zipp, country_code,
                 store_number, phone, location_type, latitude, longitude, hours.strip(), page_url]
        store = [str(x).encode('ascii', 'ignore').decode(
            'ascii').strip() if x else "<MISSING>" for x in store]

        if store[2] in addresses:
            continue
        addresses.append(store[2])
        stores.append(store)
    return stores


def crawl_city_url(url):
    if "/en/auto-parts-stores-near-me/nc/wilmington" in url['href']:
        return scrape_multiple_in_city(url)
    else:
        if "(1)" in url.text:
            return scrape_one_in_city(url)
        else:
            return scrape_multiple_in_city(url)


def fetch_data():
    state_urls = []
    city_urls = []
    soup = bs(
        get("https://www.napaonline.com/en/auto-parts-stores-near-me").text, "lxml")

    for link in soup.find("div", {"class": "store-browse-content"}).find_all("a"):
        state_urls.append(base_url+link['href'])

    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = [executor.submit(crawl_state_url, url) for url in state_urls]
        for result in as_completed(futures):
            city_urls.extend(result.result())

    log(f'found {len(city_urls)} city urls')

    # for testing with only one city ...
    # city_urls = [{
    #     'href': '/en/auto-parts-stores-near-me/nc/wilmington'
    # }]

    with ThreadPoolExecutor(max_workers=8) as executor:
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

# "https://www.napaonline.com/api/storelocator/nearby-stores?storeType=ACMEC&location=85029&sortBy=2&language=en&page=1&distanceSearch=100"
# "https://www.napaonline.com/api/storelocator/nearby-stores?storeType=ACCOL&location=85029&sortBy=2&language=en&distanceSearch=100"
# "https://www.napaonline.com/api/storelocator/nearby-stores?storeType=ACTSC&location=85029&sortBy=2&language=en&distanceSearch=100"
