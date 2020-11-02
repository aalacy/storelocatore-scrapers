import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re



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

    res=session.get("http://nashvillepetproducts.com/locations/")
    soup = BeautifulSoup(res.text, 'html.parser')
    sls = soup.find_all('section', {'id': 'jlb-locations'})
    del sls[-1]

    for s in sls:
        loc=s.find('h1').text
        ps = s.find_all('p')
        street,csz,phone=re.findall(r'</strong><br/>(.*)<br/>(.*)<br/><[emi]+>.*\"tel:(.*)\">',str(ps[0]))[0]
        csz=csz.strip().split(',')
        city= csz[0]
        csz=csz[1].strip().split(" ")
        state=csz[0]
        zip=csz[1]
        tim=ps[1].text.replace("Hours","").replace("PMS","PM S").strip()
        all.append([
            'http://nashvillepetproducts.com/',
            loc,
            street,
            city,
            state,
            zip,
            "US",
            "<MISSING>",  # store #
            phone,  # phone
            "<MISSING>",  # type
            "<MISSING>",  # lat
            "<MISSING>",  # long
            tim,  # timing
            "http://nashvillepetproducts.com/locations/"])
    return all

def scrape():
    data = fetch_data()
    write_output(data)

scrape()