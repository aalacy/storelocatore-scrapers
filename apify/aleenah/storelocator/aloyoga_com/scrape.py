
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

    res=session.get("https://www.aloyoga.com/pages/stores")
    soup = BeautifulSoup(res.text, 'html.parser')
    divs = re.findall(r'slideshowDataJson[\d] = ([^;]+)',str(soup))
    print(len(divs))
    for div in divs:
        js = json.loads(div)
        city=js['city'].split(',')[0]
        state=js['city'].split(',')[1]
        zip = js['address'].split(',')[-1].replace(state,'').replace('.','').strip()
        street=js['address'].split('<br>')[0].strip()

        all.append([
            "https://www.aloyoga.com",
            js['name'],
            street,
            city,
            state.strip(),
            zip,
            "US",
            "<MISSING>",  # store #
            js['phone'],  # phone
            "<MISSING>",  # type
            "<MISSING>",  # lat
            "<MISSING>",  # long
            ' '.join(js['hours']),  # timing
            "https://www.aloyoga.com/pages/stores"])
    return all

def scrape():
    data = fetch_data()
    write_output(data)


scrape()
