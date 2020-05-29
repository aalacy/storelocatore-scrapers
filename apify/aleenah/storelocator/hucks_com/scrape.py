import csv
import re
from bs4 import BeautifulSoup
import requests

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

    res = requests.get("https://hucks.com/locations/")
    soup = BeautifulSoup(res.text, 'html.parser')
    divs = soup.find_all('div', {'class': 'col-xl-4 col-md-6 my-3'})

    for div in divs:
        page_url.append("https://hucks.com/locations/" + div.find('div', {
            'class': "col-md py-1 flex-column d-block px-4 px-md-2 pl-xl-0 text-center-lg"}).find('a').get('href'))
        a = div.find('a', {'class': 'd-inline-block no-wrap show-on-map'})
        lat.append(a.get('data-latitude'))
        long.append(a.get('data-longitude'))
    for url in page_url:
        res = requests.get(url)
        soup = BeautifulSoup(res.text, 'html.parser')
        l = soup.find('h2', {'class': 'location-number'}).text
        locs.append(soup.find('h2', {'class': 'location-number'}).text)
        ids.append(re.findall(r'#([\d]+)', l)[0])
        street.append(soup.find('h3', {'class': 'location-address'}).text)
        addr = soup.find('div', {'class': 'location-citystatezip'}).text.split(",")
        cities.append(addr[0])
        addr = addr[1].strip().split()
        states.append(addr[0])
        zips.append(addr[1])
        ph = soup.find('div', {'class': 'location-phone'}).text.strip()
        if ph == "":
            ph = "<MISSING>"

        phones.append(ph)
        tim=re.findall(r'Hours: (.*)', soup.find('div', {'class': 'location-citystatezip pt-2 small'}).text)[0].replace('"', "").replace("\n", "")
        if tim=="":
            tim="<MISSING>"
        timing.append(tim)

    all = []
    for i in range(0, len(locs)):
        row = []
        row.append("https://hucks.com")
        row.append(locs[i])
        row.append(street[i])
        row.append(cities[i])
        row.append(states[i])
        row.append(zips[i])
        row.append("US")
        row.append(ids[i])  # store #
        row.append(phones[i])  # phone
        row.append("<MISSING>")  # type
        row.append(lat[i])  # lat
        row.append(long[i])  # long
        row.append(timing[i])  # timing
        row.append(page_url[i])  # page url

        all.append(row)
    return all

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
