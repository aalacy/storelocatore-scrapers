import csv
from bs4 import BeautifulSoup
from sgrequests import SgRequests
import re

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)
session = SgRequests()
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

    res=session.get("https://www.bandier.com/locations")
    soup = BeautifulSoup(res.text, 'html.parser')
    divs = soup.find_all('div', {'class': 'location-block__item'})
    all=[]
    for div in divs:

        data = div.text.replace('View on Google Maps','').strip().replace('\n\n\n','\n\n').replace('\n\n','\n').replace('Features: Parking, Coffee Dose Café,  and Studio B. Sign up for  workouts here','').replace('. Curbisde pickup only','').replace(' NOW OPEN! Hours of operation ','').replace('Store Hours:','').strip()
        if "coming soon" in data:
            continue
        data=data.split('\n')

        tim= data[-1]

        loc=data[0]

        if'*Currently closed in light of COVID-19.*' in data[0]:
            tim+=' *Currently closed in light of COVID-19.*'
            del data[0]
        addr = str(div.find('address').find('p')).replace('<p>', '').replace('</p>', '').split('<br/>')
        if '*Currently closed in light of COVID-19.*' in addr[0]:
            #del
            addr=str(div.find('address').find_all('p')[1]).replace('<p>','').replace('</p>','').split('<br/>')
        street=addr[0].strip()
        phone=re.findall(r'([\d\-]+)',addr[-1])[-1]
        addr=addr[1].strip().split(',')
        city=addr[0]
        addr=addr[1].strip().split(' ')
        zip=addr[1]
        state=addr[0]

        print(addr)
        all.append([
            "https://www.bandier.com/locations",
            loc,
            street,
            city,
            state.strip(),
            zip,
            "US",
            "<MISSING>",  # store #
            phone,  # phone
            "<MISSING>",  # type
            "<MISSING>",  # lat
            "<MISSING>",  # long
            tim,  # timing
            "https://www.bandier.com/locations"])

    return all

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
