import csv
from bs4 import BeautifulSoup
import requests


def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)


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
    page_url=[]

    res=requests.get("https://www.bandier.com/locations")
    soup = BeautifulSoup(res.text, 'html.parser')
    uls = soup.find('div', {'class': 'section-content'}).find_all('ul')

    for ul in uls:
        lis= ul.find_all('li')
        locs.append(lis[0].text)
        street.append(lis[1].text)
        addr=lis[2].text.split(",")
        cities.append(addr[0])
        addr=addr[1].strip().split(" ")
        states.append(addr[0])
        zips.append(addr[1])
        timing.append(lis[3].text.strip())
        if len(lis) ==5:
            phones.append(lis[4].text.replace("T: ","").strip())
        else:
            phones.append("<MISSING>")

    all = []
    for i in range(0, len(locs)):
        row = []
        row.append("https://www.bandier.com")
        row.append(locs[i])
        row.append(street[i])
        row.append(cities[i])
        row.append(states[i])
        row.append(zips[i])
        row.append("US")
        row.append("<MISSING>")  # store #
        row.append(phones[i])  # phone
        row.append("<MISSING>")  # type
        row.append("<MISSING>")  # lat
        row.append("<MISSING>")  # long
        row.append(timing[i])  # timing
        row.append("https://www.bandier.com/locations")  # page url

        all.append(row)
    return all


def scrape():
    data = fetch_data()
    write_output(data)


scrape()