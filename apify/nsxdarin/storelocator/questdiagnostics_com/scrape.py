import string
import csv
from sgrequests import SgRequests
import json
import sgzip
import time
import random
from requests_toolbelt.utils import dump

session = SgRequests()

get_headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-US,en;q=0.9,la;q=0.8',
    'Connection': 'keep-alive',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
}

post_headers = {
    'Accept': 'application/json, text/plain, */*',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-US,en;q=0.9,la;q=0.8',
    'Connection': 'keep-alive',
    'Content-Type': 'application/json',
    'Host': 'appointment.questdiagnostics.com',
    'Origin': 'https://appointment.questdiagnostics.com',
    'Referer': 'https://appointment.questdiagnostics.com/patient/findlocation',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36'
}


def debug(response):
    data = dump.dump_all(response)
    print(data.decode('utf-8'))


def sleep(min=1, max=3):
    duration = random.randint(min, max)
    time.sleep(duration)


def get_random_string(stringLength=34):
    lettersAndDigits = string.ascii_lowercase + string.digits
    return ''.join((random.choice(lettersAndDigits) for i in range(stringLength)))


def setCookie(session, domain, name, value):
  if domain is None:
    cookie_obj = session.cookies.set(name=name, value=value)
  else:
    cookie_obj = session.cookies.set(domain=domain, name=name, value=value)
  session.cookies.set_cookie(cookie_obj)


def get_f5_cookie(response):
    # this cookie isn't persisted between requests for some reason
    #   maybe because it's marked HttpOnly?
    f5_cookie = None
    for cookie in response.cookies:
        # print(cookie)
        if cookie.name.startswith('f5'):
            f5_cookie = (cookie.name, response.cookies.get(cookie.name))
            # print('f5_cookie found: ', f5_cookie)
    return f5_cookie


def visit_search_page():
    # start with search page to populate cookies
    url_home = 'https://appointment.questdiagnostics.com/patient/findlocation'
    r = session.get(url_home, headers=get_headers)
    r.raise_for_status()
    return r


def populate_demyq_cookie(previous_response):
    # this request is required in order to get the "demyq" cookie, otherwise 401 unauthorized

    csrf_token = get_random_string()
    setCookie(session.session, 'appointment.questdiagnostics.com',
              'CSRF-TOKEN', csrf_token)

    f5_cookie = get_f5_cookie(previous_response)
    if f5_cookie:
        setCookie(session.session, 'appointment.questdiagnostics.com',
                  f5_cookie[0], f5_cookie[1])

    post_headers['X-CSRF-TOKEN'] = csrf_token
    post_headers['Content-Length'] = '2'
    url_encounter = 'https://appointment.questdiagnostics.com/mq-service/asone/encounter'
    r = session.session.put(url_encounter, data='{}', headers=post_headers)
    r.raise_for_status()


def init_session():
    r = visit_search_page()
    sleep()
    populate_demyq_cookie(r)


def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip",
                         "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)


def fetch_data():
    ids = []

    search = sgzip.ClosestNSearch()
    search.initialize()
    coord = search.next_coord()

    MAX_COUNT = 100
    MAX_DISTANCE = 100

    url = 'https://appointment.questdiagnostics.com/as-service/services/getQuestLocations'

    while coord:
        x = float(coord[0])
        y = float(coord[1])
        x = str(round(x, 2))
        y = str(round(y, 2))
        # print('searching coords: %s - %s ...' % (str(x), str(y)))

        locations = []
        result_coords = []
        search_request_count = 0

        # switch IPs every 7 requests
        if search_request_count % 7 == 0:
            init_session()

        sleep()
        f5_cookie = None
        payload = '{"miles":100,"address":{},"latitude":' + str(x) + ',"longitude":' + str(
            y) + ',"serviceType":["all"],"maxReturn":100,"onlyScheduled":"false","accessType":[],"questDirect":false}'
        payload = json.loads(payload)
        payload_string = json.dumps(payload)

        csrf_token = get_random_string()
        setCookie(session.session, 'appointment.questdiagnostics.com',
                  'CSRF-TOKEN', csrf_token)
        post_headers['X-CSRF-TOKEN'] = csrf_token

        if f5_cookie:
            setCookie(session.session, 'appointment.questdiagnostics.com',
                      f5_cookie[0], f5_cookie[1])

        post_headers['Content-Length'] = str(len(payload_string))
        r = session.post(url, data=payload_string, headers=post_headers)
        r.raise_for_status()
        f5_cookie = get_f5_cookie(r)
        search_request_count = search_request_count + 1
        try:
            locations = r.json()
        except json.decoder.JSONDecodeError as err:
            if r.status_code == 204:
                # print(f'no locations found')
                search.max_distance_update(MAX_DISTANCE)
                coord = search.next_coord()
                continue
            else:
                raise
        except Exception:
            raise

        # print(f'found {len(locations)} locations')
        # print("remaining zipcodes: " + str(search.zipcodes_remaining()))

        for loc in locations:
            domain = 'questdiagnostics.com'
            name = loc['name']
            address = loc['address']
            if loc['address2']:
                address = f"{address}, {loc['address2']}"
            city = loc['city']
            state = loc['state']
            zc = loc['zip']
            phone = loc['phone']
            store_num = loc['siteCode']
            hours = loc['hoursOfOperations']

            lat = loc['latitude']
            lng = loc['longitude']
            result_coords.append((lat, lng))

            typ = loc['locationType']
            if typ == " ":
                typ = '<MISSING>'
            country = 'US'
            lurl = '<MISSING>'

            if store_num not in ids:
                ids.append(store_num)
                # print(f'Pulling Location: {store_num} ...')
                poi = [domain, lurl, name, address, city, state, zc,
                       country, store_num, phone, typ, lat, lng, hours]
                poi = [str(x).encode('ascii', 'ignore').decode(
                    'ascii').strip() if x else "<MISSING>" for x in poi]
                yield poi

        search.max_count_update(result_coords)
        coord = search.next_coord()


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
