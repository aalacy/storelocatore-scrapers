import csv
from sgrequests import SgRequests
from requests_toolbelt.utils import dump
import re
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('smartandfinal_com')




def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def debug(response):
    data = dump.dump_all(response)
    logger.info(data.decode('utf-8'))


def setCookie(session, domain, name, value):
  if domain is None:
    cookie_obj = session.cookies.set(name=name, value=value)
  else:
    cookie_obj = session.cookies.set(domain=domain, name=name, value=value)
  session.cookies.set_cookie(cookie_obj)


def fetch_data():

    addresses = []

    headers = {
        'accept': 'application/json, text/plain, */*',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.9,la;q=0.8',
        'cache-control': 'no-cache',
        'pragma': 'no-cache',
        'referer': 'https://www.smartandfinal.com/stores/?coordinates=34.62683229277248,-95.16241099999999&zoom=3',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36',
    }

    session = SgRequests()

    init_url = "https://www.smartandfinal.com/api/m_user/sessioninit"
    r = session.post(init_url, headers=headers)
    csrf_token = r.json()[0]

    setCookie(session.get_session(), 'www.smartandfinal.com', 'has_js', '1')
    setCookie(session.get_session(), 'www.smartandfinal.com',
              'XSRF-TOKEN', csrf_token)
    headers['x-csrf-token'] = csrf_token

    url = "https://www.smartandfinal.com/api/m_store_location?store_type_ids=1,2,3"
    r = session.get(url, headers=headers)

    data = r.json()

    for loc in data['stores']:
        store_number = loc['store_number']
        location_type = ''
        country_code = ''
        hours_of_operation = ''
        locator_domain = 'https://www.smartandfinal.com/'
        phone = ''
        dictionary = {}
        weekday = ['Sunday', 'Monday', 'Tuesday',
                   'Wednesday', 'Thursday', 'Friday', 'Saturday']
        for day, h in enumerate(loc['store_hours']):

            dictionary[weekday[day]] = h['open']+'-'+h['close']
        hours_of_operation = ''
        for h1 in dictionary:
            hours_of_operation = hours_of_operation + \
                ' ' + h1 + ' ' + dictionary[h1]

        phone = loc['phone']
        name = loc['storeName'].replace("-", "").replace(".", "")
        page_url = "https://www.smartandfinal.com/stores/" + \
            str(name.replace(" ", "-").lower())+"-" + \
            str(store_number)+"/"+str(loc['locationID'])

        store = [locator_domain, loc['storeName'].capitalize(), loc['address'].capitalize(), loc['city'].capitalize(), loc['state'].capitalize(), loc['zip'], country_code,
                 store_number, phone, location_type, loc['latitude'], loc['longitude'], hours_of_operation, page_url]

        if str(store[2]) + str(store[-3]) not in addresses:
            addresses.append(str(store[2]) + str(store[-3]))

            store = [str(x).encode('ascii', 'ignore').decode(
                'ascii').strip() if x else "<MISSING>" for x in store]

            # logger.info("data = " + str(store))
            # logger.info('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
            yield store
            # logger.info("-----------------------------------",store)


def scrape():
    data = fetch_data()
    write_output(data)


scrape()

