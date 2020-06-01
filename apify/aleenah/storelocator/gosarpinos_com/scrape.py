import csv
import re
from bs4 import BeautifulSoup
from sgrequests import SgRequests

session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def get_stores():
    HEADERS = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36'
    }
    response = session.get('https://www.gosarpinos.com/api/stores', headers=HEADERS).json()
    return [('https://www.gosarpinos.com/' + x['storeUrl'], x['state'], x['name'], x['id']) for x in response]

def handle_missing(x):
    if not x.strip():
        return '<MISSING>'
    return x

def sanitize(x):
    return handle_missing(x.strip().replace("’", "'").replace("&#39;", "'"))

def fetch_data():
    # Your scraper here
    locs = []
    street = []
    states=[]
    cities = []
    types=[]
    phones = []
    zips = []
    long = []
    lat = []
    timing = []
    ids=[]
    page_urls = []

    stores = get_stores()
    for store in stores:
        states.append(store[1])
        locs.append(store[2])
        ids.append(store[3])
        url = store[0]
        page_urls.append(url)
        res = session.get(url)
        soup = BeautifulSoup(res.text, 'html.parser')
        script = soup.find_all("script")[-1].text.split('"intId"')
        days = re.findall(r'"day":"([^"]+)"', script[0])
        shed = re.findall(r'"workingHours":"([^"]+)"', script[0])
        tim = ""

        for i in range(7):
            tim += days[i] + " " + shed[i] + " "

        timing.append(tim)
        script=script[1]
        street.append(re.findall(r'"address":"([^"]+),"',script)[0])
        cities.append(re.findall(r'"city":"([^"]+)"',script)[0])
        zips.append(re.findall(r'"postalCode":"([^"]+)"',script)[0])
        phones.append(re.findall(r'"phone":"([^"]+)"',script)[0])
        lat.append(re.findall(r'"latitude":(-?[\d\.]*)',script)[0])
        long.append(re.findall(r'"longitude":(-?[\d\.]*)',script)[0])

    all = []
    for i in range(0, len(stores)):
        row = []
        row.append("https://www.gosarpinos.com")
        row.append(sanitize(locs[i]))
        row.append(sanitize(street[i]))
        row.append(sanitize(cities[i]))
        row.append(sanitize(states[i]))
        row.append(sanitize(zips[i]))
        row.append("US")
        row.append(ids[i])  # store #
        row.append(sanitize(phones[i]))  # phone
        row.append("<MISSING>")  # type
        row.append(sanitize(lat[i]))  # lat
        row.append(sanitize(long[i]))  # long
        row.append(sanitize(timing[i]))  # timing
        row.append(handle_missing(page_urls[i]))  # page url

        all.append(row)
    return all

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
