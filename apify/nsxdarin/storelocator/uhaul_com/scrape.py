import csv
from sgrequests import SgRequests
import time
import random
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from ssl import SSLError


thread_local = threading.local()

headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
    'connection': 'Keep-Alive'
}


def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip",
                         "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)


def random_sleep():
    time.sleep(random.random()*2)


def get_session(reset=False):
    # give each thread its own session object
    # if using proxy, each thread's session should have a unique IP
    if (not hasattr(thread_local, "session")) or (reset==True):
        thread_local.session = SgRequests()
    return thread_local.session


def get_state_urls():
    state_urls = []
    session = get_session()
    url = 'https://www.uhaul.com/Locations/US_and_Canada/'
    r = session.get(url, headers=headers)
    for line in r.iter_lines(decode_unicode=True):
        if "<a href='/Locations/" in line:
            lurl = 'https://www.uhaul.com' + \
                line.split("href='")[1].split("'")[0]
            state_urls.append(lurl)
    return state_urls


def get_city_urls(state_urls):
    cities_all = []
    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = [executor.submit(get_cities_in_state, url)
                   for url in state_urls]
        for result in as_completed(futures):
            cities_all.extend(result.result())
    return cities_all


def get_cities_in_state(state_url):
    cities = []
    session = get_session()

    #print('Pulling State %s ...' % state_url)
    random_sleep()
    try:
      r = session.get(state_url, headers=headers)
    except SSLError:
      session = get_session(reset=True)
      r = session.get(state_url, headers=headers)
    #print('status: ', r.status_code)

    for line in r.iter_lines(decode_unicode=True):
        if "<a href='/Locations/" in line:
            lurl = 'https://www.uhaul.com' + \
                line.split("href='")[1].split("'")[0]
            if lurl not in cities:
                cities.append(lurl)

    return cities


def get_location_urls(city_urls):
    locations_all = []

    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = [executor.submit(get_locations_in_city, url)
                   for url in city_urls]
        for result in as_completed(futures):
            locations_all.extend(result.result())

    return locations_all


def get_locations_in_city(city_url):
    locs = []
    session = get_session()
    allids = []
    coords = []
    alllocs = []
    #print('Pulling City %s ...' % city_url)
    try: 
      r2 = session.get(city_url, headers=headers)
    except SSLError:
      session = get_session(reset=True)
      r2=session.get(city_url, headers=headers)
    #print('status: ', r2.status_code)
    lines = r2.iter_lines(decode_unicode=True)
    for line2 in lines:
        if '"entityNum":"' in line2:
            items = line2.split('"lat":')
            for item in items:
                if '"entityNum":"' in item:
                    lat = item.split(',')[0]
                    lng = item.split('"long":')[1].split(',')[0]
                    pid = item.split('"entityNum":"')[1].split('"')[0]
                    coords.append(pid + '|' + lat + '|' + lng)
        if '<ul class="sub-nav ">' in line2:
            try:
                next(lines)
                g = next(lines)
                if 'href="' not in g:
                    g = next(lines)
                lurl = g.split('href="')[1].split('/"')[0]
                if 'http' not in lurl:
                    lurl = 'https://www.uhaul.com' + lurl
                enum = lurl.rsplit('/', 1)[1]
                alllocs.append(lurl + '|' + enum)
            except StopIteration:
                break

    for location in alllocs:
        for place in coords:
            if location.split('|')[1] == place.split('|')[0]:
                plat = place.split('|')[1]
                plng = place.split('|')[2]
                lurl = location.split('|')[0]
                lid = lurl.rsplit('/', 1)[1]
                lurl = 'https://www.uhaul.com/Locations/Truck-Rentals/' + lid
                if lid not in allids:
                    allids.append(lid)
                    locs.append(lurl + '|' + plat + '|' + plng)

    return locs


def fetch_data():

    states = get_state_urls()
    cities = get_city_urls(states)
    locs = get_location_urls(cities)

    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = [executor.submit(get_location, loc) for loc in locs]
        for result in as_completed(futures):
            record = result.result()
            if record is not None:
                yield record


def get_location(loc):

    session = get_session()
    #print('Pulling Location %s ...' % loc.split('|')[0])
    website = 'uhaul.com'
    typ = ''
    hours = ''
    name = ''
    add = ''
    city = ''
    state = ''
    zc = ''
    country = ''
    store = ''
    phone = ''
    lat = loc.split('|')[1]
    lng = loc.split('|')[2]
    lurl = loc.split('|')[0]
    store = lurl.rsplit('/', 1)[1]

    try:
      r2 = session.get(lurl, headers=headers, timeout=5)
    except SSLError:
      session = get_session(reset=True)
      r2 = session.get(lurl, headers=headers, timeout=5)
    #print('status: ', r2.status_code)

    for line2 in r2.iter_lines(decode_unicode=True):
        if '<small class="text-light">(' in line2 and 'all room' not in line2:
            typ = line2.split('<small class="text-light">(')[1].split(')')[0]
        if ',"addressRegion":"' in line2:
            state = line2.split(',"addressRegion":"')[1].split('"')[0]
            name = line2.split('"name":"')[1].split('"')[0]
            country = line2.split(',"addressCountry":"')[1].split('"')[0]
            if 'United' in country:
                country = 'US'
            if 'Canada' in country:
                country = 'CA'
            city = line2.split('"addressLocality":"')[1].split('"')[0]
            zc = line2.split('"postalCode":"')[1].split('"')[0]
            add = line2.split('"streetAddress":"')[1].split('"')[0]
            phone = line2.split('"telephone":"')[1].split('"')[0]
            hours = line2.split('"openingHours":')[
                1].split(',"aggregateRating')[0]
            hours = hours.replace('[', '').replace(']', '').replace(
                '","', '; ').replace('"', '')
    if hours == '':
        hours = '<MISSING>'
    if typ == '':
        typ = 'U-Haul'
    if phone == '':
        phone = '<MISSING>'
    if add != '':
        return [website, lurl, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
