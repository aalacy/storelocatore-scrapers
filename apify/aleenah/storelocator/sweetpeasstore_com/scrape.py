import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
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

all=[]
def fetch_data():
    # Your scraper here

    res = session.get('https://sweetpeasstore.com/locations/')
    soup = BeautifulSoup(res.text, 'html.parser')
    stores=json.loads(re.findall(r'wpgmaps_localize_marker_data = ([^;]+)',str(soup))[0])

    for store in stores:

        addr=stores[store]['address'].replace(', USA','').split(',')
        sz=addr[-1]
        zip=re.findall('[\d]{5}',sz)
        if zip ==[]:
            zip='<MISSING>'
        else:
            zip=zip[0]
        state=sz.replace(zip,'').strip()
        del addr[-1]
        city= addr[-1].strip()
        del addr[-1]
        street=', '.join(addr)

        lat=stores[store]['lat']
        long=stores[store]['lng']

        all.append([
                "https://www.zipsdrivein.com",
                '<MISSING>',
                street,
                city,
                state,
                zip,
                'US',
                '<MISSING>',  # store #
                '<MISSING>',  # phone
                "<MISSING>",  # type
                lat,  # lat
                long,  # long
                '<MISSING>',  # timing
                'https://www.zipsdrivein.com/locations/'])

    return all

def scrape():
    data = fetch_data()
    write_output(data)


scrape()