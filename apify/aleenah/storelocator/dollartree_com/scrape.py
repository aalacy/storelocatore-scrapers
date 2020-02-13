import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import json

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation",
                         "page_url"])
        # Body
        for row in data:
            writer.writerow(row)


session = SgRequests()


def fetch_data():
    # Your scraper here
    locs = []
    street = []
    states = []
    cities = []
    types = []
    phones = []
    zips = []
    long = []
    lat = []
    timing = []
    ids = []
    page_url = []
    countries = []

    res=session.get("https://www.dollartree.com/locations/")
    soup = BeautifulSoup(res.text, 'html.parser')
    sls = soup.find('div', {'class': 'content_area'}).find_all('a')
    print(len(sls))
    for sl in sls:
        res = session.get(sl.get('href'))
        soup = BeautifulSoup(res.text, 'html.parser')
        cls = soup.find('div', {'class': 'content_area'}).find_all('a')
        print(len(cls))
        for cl in cls:
            res = session.get(cl.get('href'))
            soup = BeautifulSoup(res.text, 'html.parser')
            pls = soup.find_all('div', {'class': 'storeinfo_div '})
            print(len(pls))
            for p in pls:
                page_url.append(p.get('href'))
                print(p.get('href'))

fetch_data()