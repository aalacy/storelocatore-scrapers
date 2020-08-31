import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import sgzip
import time



session = SgRequests()

def request_wrapper(url, method, headers, data=None):
  request_counter = 0
  if method == "get":
    while True:
      try:
        r = session.get(url, headers=headers)
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
          r = session.post(url, headers=headers, data=data)
        else:
          r = session.post(url, headers=headers)
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
  # search.initialize()
  search.initialize(include_canadian_fsas=True)
  MAX_RESULTS = 11
  MAX_DISTANCE = 50
  coord = search.next_coord()
  # zip_code = search.next_zip()
  while coord:
    result_coords = []
    # x = coord[0]
    # y = coord[1]
    #print("remaining zipcodes: " + str(search.zipcodes_remaining()))
    # print("zipcode == " + str(zip_code))
    time.sleep(1)
    r = request_wrapper("https://www.dvf.com/on/demandware.store/Sites-DvF_US-Site/default/Stores-FinderJSON?lat=" +
                        str(coord[0]) + "&lng=" + str(coord[1]) + "&showRP=true&showOutlet=false", "get", headers=headers)
    data = r.json()
    for state_data in data['results']:
      for store_data in state_data["stores"]:
        store = []
        store.append("https://www.dvf.com")
        store.append(store_data["name"])
        store.append(store_data["address1"] + " " + store_data['address2']
                     if store_data["address2"] != None else store_data["address1"])
        if store[-1] in addresses:
          continue
        addresses.append(store[-1])
        store.append(store_data["city"])
        store.append(store_data["stateCode"])
        #print(store_data["postalCode"])
        store.append(store_data["postalCode"])
        store.append(store_data["countryCode"])
        store.append(store_data["id"])
        store.append(store_data["phone"] if store_data["phone"]
                     != "" and store_data["phone"] != None else "<MISSING>")
        store.append("<MISSING>")
        store.append(store_data["latitude"])
        store.append(store_data["longitude"])
        result_coords.append((store_data["latitude"], store_data["longitude"]))

        hours = " ".join(
            list(BeautifulSoup(store_data["storeHours"], "lxml").stripped_strings))
        store.append(hours if hours != "" else "<MISSING>")
        store.append("<MISSING>")
        return_main_object.append(store)
        #print("data==" + str(store))
        #print('~~~~~~~~~~~~~~~~~~~~~`')
        yield store

    if len(data['results']) < MAX_RESULTS:
      # print("max distance update")
      search.max_distance_update(MAX_DISTANCE)
    # if len(data['results']) == MAX_RESULTS:
    #   # print("max count update")
    #   search.max_count_update(result_coords)
    # else:
    #   raise Exception("expected at most " + str(MAX_RESULTS) + " results")
    coord = search.next_coord()


def scrape():
  data = fetch_data()
  write_output(data)


scrape()
