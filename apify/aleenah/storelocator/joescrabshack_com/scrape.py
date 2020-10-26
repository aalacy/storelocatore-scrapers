import csv
import re
from bs4 import BeautifulSoup
import requests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('joescrabshack_com')



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

    res=requests.get("https://www.joescrabshack.com/locations/all")
    soup = BeautifulSoup(res.text, 'html.parser')
    divs = soup.find_all('div', {'class': 'loc-results-box'})
    divs=divs[45:]
    logger.info(len(divs))
    for div in divs:
        a = div.find("h4").find('a')
        ids.append(a.get('href').split("/")[-1])
        locs.append(a.text)
        sa = div.find_all("a")
        a=sa[1]
        coord = a.get("href")
        lat.append(re.findall(r'q=(-?[\d\.]*)',coord)[0])
        long.append(re.findall(r'q=[-?\d\.]*,([-?\d\.]*)',coord)[0])
        addr=a.text.replace("\r","").split("\n")
        street.append(addr[1].strip())
        addr=addr[2].strip().split(",")
        cities.append(addr[0])
        addr=addr[1].strip().split(" ")
        states.append(addr[0])
        zips.append(addr[1])
        a=sa[2]
        phones.append(a.text.strip())
        spans=div.find_all('span')
        tim=""
        for span in spans:
            tim+=span.text+" "
        timing.append(tim)

    all = []
    for i in range(0, len(locs)):
        row = []
        row.append("https://www.joescrabshack.com")
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
        row.append("https://www.joescrabshack.com/locations/all")  # page url

        all.append(row)
    return all

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
