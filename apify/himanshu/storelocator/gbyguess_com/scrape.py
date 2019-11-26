import csv
import requests
from bs4 import BeautifulSoup
import re
import json
import sgzip
import time
import time


def request_wrapper(url, method, headers, data=None):
  request_counter = 0
  if method == "get":
    while True:
      try:
        r = requests.get(url, headers=headers)
        return r
        break
      except:
        time.sleep(2)
        request_counter = request_counter + 1
        if request_counter > 10:
          return None
          break
  elif method == "post":
    while True:
      try:
        if data:
          r = requests.post(url, headers=headers, data=data)
        else:
          r = requests.post(url, headers=headers)
        return r
        break
      except:
        time.sleep(2)
        request_counter = request_counter + 1
        if request_counter > 10:
          return None
          break
  else:
    return None


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


def fetch_data():
  headers = {
      'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
  }

  return_main_object = []
  addresses = []
  search = sgzip.ClosestNSearch()
  search.initialize()
  MAX_RESULTS = 50
  MAX_DISTANCE = 120
  coord = search.next_coord()
  zip_code = search.next_zip()
  while zip_code:
    result_coords = []
    # print("remaining zipcodes: " + str(len(search.zipcodes)))
    # print('Pulling Lat-Long %s,%s...' % (str(x), str(y)))
    time.sleep(1)
    r = request_wrapper("https://maps.stores.guess.com.prod.rioseo.com/api/getAsyncLocations?template=search&level=search&search=" +
                        str(zip_code), "get", headers=headers)
    json_data = json.loads(r.text)
    if json_data['markers'] != None:
      for location_list in json_data['markers']:
        locator_domain = 'https://www.gbyguess.com/'
        store_number = location_list['locationId']
        country_code = "US"
        info = BeautifulSoup(location_list['info'], 'lxml')
        json_info = json.loads(info.text)
        street_address = json_info['address_1'] + " " + json_info['address_2']
        city = json_info['city']
        state = json_info['region']
        zipp_list = json_info['post_code']
        ca_zip_list = re.findall(
            r'[A-Z]{1}[0-9]{1}[A-Z]{1}\s*[0-9]{1}[A-Z]{1}[0-9]{1}', str(zipp_list))
        us_zip_list = re.findall(re.compile(
            r"\b[0-9]{5}(?:-[0-9]{4})?\b"), str(zipp_list))
        if us_zip_list:
          zipp = us_zip_list[0]
          country_code = "US"
        elif ca_zip_list:
          zipp = ca_zip_list[0]
          country_code = "CA"
        else:
          continue

        location_name = json_info['location_name']
        location_type = json_info['store_type_cs']
        latitude = json_info['lat']
        longitude = json_info['lng']
        page_url = json_info['url']
        # website = json_info['website']
        r = requests .get(page_url)
        soup = BeautifulSoup(r.text, 'lxml')
        loc_hours = soup.find(
            'div', class_='hours-wrapper right').find('div', class_='hours')
        list_hours = list(loc_hours.stripped_strings)
        hours_of_operation = " ".join(list_hours)
        phone = soup.find('a', class_='phone ga-link').text.strip()
        result_coords.append((latitude, longitude))
        if street_address in addresses:
          continue

        addresses.append(street_address)

        store = []
        store.append(locator_domain if locator_domain else '<MISSING>')
        store.append(location_name if location_name else '<MISSING>')
        store.append(street_address if street_address else '<MISSING>')
        store.append(city if city else '<MISSING>')
        store.append(state if state else '<MISSING>')
        store.append(zipp if zipp else '<MISSING>')
        store.append(country_code if country_code else '<MISSING>')
        store.append(store_number if store_number else '<MISSING>')
        store.append(phone if phone else '<MISSING>')
        store.append(location_type if location_type else '<MISSING>')
        store.append(latitude if latitude else '<MISSING>')
        store.append(longitude if longitude else '<MISSING>')
        store.append(hours_of_operation if hours_of_operation else '<MISSING>')
        store.append(page_url if page_url else "<MISSING>")
        # print("===", str(store))
        # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
        # return_main_object.append(store)
        yield store
    if len(location_list) < MAX_RESULTS:
      # print("max distance update")
      search.max_distance_update(MAX_DISTANCE)
    elif len(location_list) == MAX_RESULTS:
      # print("max count update")
      search.max_count_update(result_coords)
    else:
      raise Exception("expected at most " + str(MAX_RESULTS) + " results")
    # if len(location_list) == MAX_RESULTS:
    #   # print("max count update")
    #   search.max_count_update(result_coords)
    # else:
    #   raise Exception("expected at most " + str(MAX_RESULTS) + " results")
    zip_code = search.next_zip()


def scrape():
  data = fetch_data()
  write_output(data)


scrape()
