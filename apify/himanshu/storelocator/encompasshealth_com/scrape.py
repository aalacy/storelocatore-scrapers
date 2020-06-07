import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json


def override_retries():
    # monkey patch sgrequests in order to set max retries
    import requests

    def new_init(self):
        requests.packages.urllib3.disable_warnings()
        self.session = self.requests_retry_session(retries=0)

    SgRequests.__init__ = new_init


override_retries()
session = SgRequests()
show_logs = False


def log(*args, **kwargs):
  if (show_logs == True):
    print(" ".join(map(str, args)), **kwargs)
    print("")


def write_output(data):
    with open('data.csv', mode='w', newline='') as output_file:
        writer = csv.writer(output_file, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def get_hours(store):
    page_url = store[-1]
    r1 = None
    try:
        log('getting page: ' + page_url)
        r1 = session.get(page_url)
        r1.raise_for_status()
        log('status: ', r1.status_code)
    except Exception as ex:
        log('Exception getting: ' + page_url)
        log(ex)
        # pass

    try:
        soup1 = BeautifulSoup(r1.text, "lxml")
        hours = " ".join(list(soup1.find("div", {"class": "col-lg-12 col-sm-6 col-lg-12"}).find(
            "ul").find("li", {"class": "info-mb"}).stripped_strings))
    except:
        hours = "<MISSING>"

    log('hours: ', hours)
    store[-2] = hours
    return store


def get_location(data):
    base_url = "https://encompasshealth.com"
    location_name = data['title']
    log(location_name)
    try:
        street_address = (data['address']['address1'] + " " + str(data['address']['address2'])
                          ).replace("None", "").replace("2nd Floor", "").replace(",", "").strip()
    except:
        street_address = "<MISSING>"
    if "Suite" in street_address:
        street_address = street_address.split("Suite")[0]
    city = data['address']['city']
    state = data['address']['state']
    zipp = data['address']['zip']
    if zipp:
        zipp = zipp.replace(".", "").replace("178603", "78603")
    try:
        phone = data['phone'][0]['value']
    except:
        phone = "<MISSING>"
    latitude = data['coordinates']['latitude']
    longitude = data['coordinates']['longitude']
    page_url = base_url + data['urls'][0]['link']
    hours = "<MISSING>"

    store = []
    store.append(base_url)
    store.append(location_name)
    store.append(street_address)
    store.append(city)
    store.append(state)
    store.append(zipp if zipp else "<MISSING>")
    store.append("US")
    store.append("<MISSING>")
    store.append(phone)
    store.append("<MISSING>")
    store.append(latitude)
    store.append(longitude)
    store.append(hours)
    store.append(page_url)

    store = [x.replace("–", "-") if type(x) == str else x for x in store]
    store = [str(x).encode('ascii', 'ignore').decode(
        'ascii').strip() if x else "<MISSING>" for x in store]
    # log("data == "+str(store))
    # log("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    return store


def fetch_data():
    addresses = []
    stores = []
    json_data = session.get("https://encompasshealth.com/api/locationservice/locationsearchresults/no_facet/21.190439,72.87756929999999/1000/1/75000").json()[
        'data']['locationDetailsSearchResponse']

    # parse the json for most stores info
    for data in json_data:
        store = get_location(data)
        if store and store[2] not in addresses:
            addresses.append(store[2])
            stores.append(store)

    # visit each detail page to get store hours
    for store in stores:
        store = get_hours(store)
        yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
