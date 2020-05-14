import csv
from sgrequests import SgRequests
import json
import sgzip
import time
import random
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

thread_local = threading.local()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip",
                         "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def sleep(min=1, max=5):
    duration = random.randint(min, max)
    time.sleep(duration)

def get_session():
  # give each thread its own session object.
  # when using proxy, each thread's session will have a unique IP
  #   and we'll switch IPs every 10 requests
  if (not hasattr(thread_local, "session")) or (hasattr(thread_local, "request_count") and thread_local.request_count == 10):
    thread_local.session = SgRequests()
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


def get_stores_from_coords(coord, radius, maxResults):
    headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "en-US,en;q=0.9,la;q=0.8",
        "cache-control": "max-age=0",
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "none",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36"
    }

    lat, lng = coord[0], coord[1]

    url = 'https://www.mcdonalds.com/googleapps/GoogleRestaurantLocAction.do?method=searchLocation' + \
        '&latitude=' + str(lat) + '&longitude=' + str(lng) + '&radius=' + str(radius) + '&maxResults=' + str(maxResults) + \
        '&country=gb&language=en-gb&showClosed=&hours24Text=Open%2024%20hr'

    sleep()

    session = get_session()
    r = session.get(url, headers=headers)
    json = r.json()

    store_results = []

    for item in json['features']:
        name = item['properties']['name']
        add = item['properties']['addressLine1']
        add = add + ' ' + item['properties']['addressLine2']
        add = add.strip()
        country = 'GB'
        city = item['properties']['addressLine3']
        state = '<MISSING>'
        zc = item['properties']['postcode']
        phone = item['properties']['telephone']
        website = 'mcdonalds.co.uk'
        try:
            hours = 'Mon: ' + \
                item['properties']['restauranthours']['hoursMonday']
            hours = hours + '; Tue: ' + \
                item['properties']['restauranthours']['hoursTuesday']
            hours = hours + '; Wed: ' + \
                item['properties']['restauranthours']['hoursWednesday']
            hours = hours + '; Thu: ' + \
                item['properties']['restauranthours']['hoursThursday']
            hours = hours + '; Fri: ' + \
                item['properties']['restauranthours']['hoursFriday']
            hours = hours + '; Sat: ' + \
                item['properties']['restauranthours']['hoursSaturday']
            hours = hours + '; Sun: ' + \
                item['properties']['restauranthours']['hoursSunday']
        except:
            hours = '<MISSING>'
        typ = 'Restaurant'
        loc = '<MISSING>'
        store_number = item['properties']['identifiers']['storeIdentifier'][1]['identifierValue']
        lat = item['geometry']['coordinates'][0]
        lng = item['geometry']['coordinates'][1]
        if phone == '':
            phone = '<MISSING>'
        if city == '':
            city = '<MISSING>'

        store_results.append([website, loc, name, add, city, state,
                              zc, country, store_number, phone, typ, lat, lng, hours])

    increment_request_count()

    return store_results


def fetch_data():
    radius = 10
    maxResults = 25
    unique_store_ids = []

    search = sgzip.ClosestNSearch()
    search.initialize(country_codes=['gb'])

    all_coords = []
    coord = search.next_coord()
    all_coords.append(coord)
    while coord:
      coord = search.next_coord()
      all_coords.append(coord)

    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = [executor.submit(
            get_stores_from_coords, coord, radius, maxResults) for coord in all_coords]
        for result in as_completed(futures):
            try:
              stores_returned = result.result()
              for store in stores_returned:
                  identifier = f'{store[8]}-{store[3]}'.replace(' ', '')
                  if identifier not in unique_store_ids:
                      unique_store_ids.append(identifier)
                      yield store
            except Exception as exc:
              print('---- exception ----: %s' % (exc))

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
