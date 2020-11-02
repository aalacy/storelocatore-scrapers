import csv
from urllib.request import urlopen
from sgrequests import SgRequests
import gzip
import os
import time
import random
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from requests.exceptions import RequestException
import requests_random_user_agent
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('westernunion_com')




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
        r = session.get(url, headers=headers)
        r.raise_for_status()

        increment_request_count()

    except (RequestException, OSError) as err:
        # attempt to handle errors such as "cannot connect to proxy, timed out"
        log(f'***** error getting {url} on thread {threading.current_thread().ident}')
        log(err)
        log('****** resetting session')
        session = get_session(reset=True)
        # try this request again
        return get(url)

    return r


def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)


def get_location(loc):
    website = 'westernunion.com'
    typ = 'Location'
    store = '<MISSING>'
    hours = '<MISSING>'
    city = ''
    add = ''
    state = ''
    zc = ''
    if '/us/' in loc:
        country = 'US'
    if '/ca/' in loc:
        country = 'CA'
    name = ''
    phone = ''
    lat = ''
    lng = ''
    store = loc.rsplit('/', 1)[1]
    loc = loc.replace('http://', 'https://')
    log('Pulling Location %s... ' % loc)
    r = get(loc)
    lines = r.iter_lines(decode_unicode=True)
    AFound = False
    for line in lines:
        if '"name":"' in line:
            name = line.split('"name":"')[1].split('"')[0]
        if '"streetAddress":"' in line and AFound is False:
            AFound = True
            add = line.split('"streetAddress":"')[1].split('"')[0]
        if '"city":"' in line:
            city = line.split('"city":"')[1].split('"')[0]
        if '"state":"' in line:
            state = line.split('"state":"')[1].split('"')[0]
        if '"postal":"' in line:
            zc = line.split('"postal":"')[1].split('"')[0]
        if '"geoQualitySort":' in line:
            phone = line.split('"geoQualitySort":')[1].split(
                '"phone":"')[1].split('"')[0]
        if '"latitude":' in line:
            lat = line.split('"latitude":')[1].split(',')[0]
        if '"longitude":' in line:
            lng = line.split('"longitude":')[1].split(',')[0]
        if '"monCloseTime":"' in line:
            hours = 'Mon: ' + line.split('"monOpenTime":"')[1].split(
                '"')[0] + '-' + line.split('"monCloseTime":"')[1].split('"')[0]
            hours = hours + '; Tue: ' + line.split('"tueOpenTime":"')[1].split(
                '"')[0] + '-' + line.split('"tueCloseTime":"')[1].split('"')[0]
            hours = hours + '; Wed: ' + line.split('"wedOpenTime":"')[1].split(
                '"')[0] + '-' + line.split('"wedCloseTime":"')[1].split('"')[0]
            hours = hours + '; Thu: ' + line.split('"thuOpenTime":"')[1].split(
                '"')[0] + '-' + line.split('"thuCloseTime":"')[1].split('"')[0]
            hours = hours + '; Fri: ' + line.split('"friOpenTime":"')[1].split(
                '"')[0] + '-' + line.split('"friCloseTime":"')[1].split('"')[0]
            hours = hours + '; Sat: ' + line.split('"satOpenTime":"')[1].split(
                '"')[0] + '-' + line.split('"satCloseTime":"')[1].split('"')[0]
            hours = hours + '; Sun: ' + line.split('"sunOpenTime":"')[1].split(
                '"')[0] + '-' + line.split('"sunCloseTime":"')[1].split('"')[0]
    return [website, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]


def fetch_data():
    locs = []
    for x in range(1, 15):
        log('Pulling Sitemap %s...' % str(x))
        smurl = 'http://locations.westernunion.com/sitemap-' + \
            str(x) + '.xml.gz'
        with open('branches.xml.gz', 'wb') as f:
            f.write(urlopen(smurl).read())
            f.close()
            with gzip.open('branches.xml.gz', 'rt') as f:
                for line in f:
                    if '<loc>http://locations.westernunion.com/us/' in line:
                        locs.append(line.split('<loc>')[1].split('<')[0])
        log(str(len(locs)) + ' Locations Found...')

    with ThreadPoolExecutor(max_workers=16) as executor:
        futures = [executor.submit(get_location, url) for url in locs]
        for result in as_completed(futures):
            location = result.result()
            if location:
                yield location


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
