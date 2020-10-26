import csv
from sgrequests import SgRequests
import time
import random
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from ssl import SSLError
import html
from bs4 import BeautifulSoup
import re
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('riteaid_com')




thread_local = threading.local()

headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
    'connection': 'Keep-Alive'
}


def sleep(min=1, max=3):
    duration = random.randint(min, max)
    time.sleep(duration)


def get_session(reset=False):
    # give each thread its own session object
    # if using proxy, each thread's session should have a unique IP
    if (not hasattr(thread_local, "session")) or (reset == True):
        thread_local.session = SgRequests()
    return thread_local.session


def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip",
                         "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)


def enqueue_links(url):

    # logger.info('getting links from ' + url)

    locs = []
    cities = []
    states = []

    session = get_session()
    r = session.get(url, headers=headers)

    soup = BeautifulSoup(r.text, 'html.parser')
    dir_links = soup.select('a.c-directory-list-content-item-link')
    for link in dir_links:
        lurl = 'https://locations.riteaid.com.yext-cdn.com/' + link['href']
        if lurl.count('/') == 5:
            locs.append(lurl)
        elif lurl.count('/') == 4:
            cities.append(lurl)
        else:
            states.append(lurl)

    store_links = soup.select('h5.c-location-grid-item-title a')
    for link in store_links:
        lurl = 'https://locations.riteaid.com.yext-cdn.com/' + \
            re.sub(r'^\.\.\/', '', link['href'])  # remove "../" at beginning
        locs.append(lurl)

    d = dict()
    d['locs'] = locs
    d['cities'] = cities
    d['states'] = states

    return d


def scrape_state_urls(state_urls, city_urls, loc_urls):
    # scrape each state url and populate city_urls and loc_urls with the results
    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = [executor.submit(enqueue_links, url) for url in state_urls]
        for result in as_completed(futures):
            d = result.result()
            city_urls.extend(d['cities'])
            loc_urls.extend(d['locs'])


def scrape_city_urls(city_urls, loc_urls):
    # scrape each city url and populate loc_urls with the results
    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = [executor.submit(enqueue_links, url) for url in city_urls]
        for result in as_completed(futures):
            d = result.result()
            loc_urls.extend(d['locs'])


def get_location(loc):
    # logger.info('Pulling Location %s ...' % loc)
    session = get_session()
    website = 'riteaid.com'
    typ = 'RiteAid'
    name = ''
    add = ''
    city = ''
    state = ''
    country = 'US'
    zc = ''
    store = '<MISSING>'
    phone = ''
    lat = ''
    lng = ''
    hours = ''
    # sleep()
    r2 = session.get(loc, headers=headers)
    for line2 in r2.iter_lines(decode_unicode=True):
        if 'data-storeid="' in line2:
            store = line2.split('data-storeid="')[1].split('"')[0]
        if 'id="location-name">' in line2:
            name = line2.split(
                'id="location-name">')[1].split('<')[0]
        if '<meta itemprop="latitude" content="' in line2:
            lat = line2.split('<meta itemprop="latitude" content="')[
                1].split('"')[0]
            lng = line2.split('<meta itemprop="longitude" content="')[
                1].split('"')[0]
        if " 'dimension4', '" in line2:
            #add = line2.split(" 'dimension4', '")[1].split("'")[0]
            zc = line2.split("dimension5', '")[1].split("'")[0]
            state = line2.split("'dimension2', '")[1].split("'")[0]
            city = line2.split("'dimension3', '")[1].split("'")[0]
            city = html.unescape(city)
        if 'itemprop="telephone" id="telephone">' in line2:
            phone = line2.split('itemprop="telephone" id="telephone">')[
                1].split('<')[0]
        if hours == '' and "data-days='[{" in line2:
            days = line2.split(
                "data-days='[{")[1].split(']}]')[0].split('"day":"')
            for day in days:
                if '"intervals":' in day:
                    try:
                        hrs = day.split('"')[0] + ': ' + day.split(',"start":')[1].split('}')[
                            0] + '-' + day.split('"end":')[1].split(',')[0]
                    except:
                        hrs = day.split('"')[0] + ': Closed'
                    if hours == '':
                        hours = hrs
                    else:
                        hours = hours + '; ' + hrs
        if '<span class="c-address-street-1">' in line2:
            add = line2.split(
                '<span class="c-address-street-1">')[1].split('<')[0].strip()
            if '<span class="c-address-street-2">' in line2:
                add = add + ' ' + \
                    line2.split(
                        '<span class="c-address-street-2">')[1].split('<')[0].strip()
    if hours == '':
        hours = '<MISSING>'
    if 'closed' in name.lower():
        # logger.info('skipping closed store: ', loc)
        pass
    else:
        if store != '':
            hours = hours.replace('-0', '-0000')
            if phone == '':
                phone = '<MISSING>'
            if 'RediClinic' in name:
                typ = 'RediClinic'
            return [website, loc.replace('https://locations.riteaid.com.yext-cdn.com/', 'https://www.riteaid.com/locations/'), name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]


def fetch_data():

    d = enqueue_links('https://locations.riteaid.com.yext-cdn.com/')

    state_urls = d['states']
    city_urls = d['cities']
    loc_urls = d['locs']

    scrape_state_urls(state_urls, city_urls, loc_urls)

    scrape_city_urls(city_urls, loc_urls)

    # logger.info('loc_urls: ', len(loc_urls))

    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = [executor.submit(get_location, loc) for loc in loc_urls]
        for result in as_completed(futures):
            record = result.result()
            if record is not None:
                yield record


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
