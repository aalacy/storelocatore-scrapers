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

    res=session.get("https://www.miranchitorestaurants.com/")
    soup = BeautifulSoup(res.text, 'html.parser')
    scripts = soup.find_all('script', {'type': 'application/ld+json'})
    for script in scripts:
        jso = json.loads(re.findall(r'{.*}',str(script))[0])
        tim=' '.join(jso['openingHours']).replace('Mo','Monday').replace('Tu','Tuesday').replace('We','Wednesday').replace('Th','Thursday').replace('Fr','Friday').replace('Sa','Saturday').replace('Su','Sunday').strip()
        loc=jso['address']['addressLocality']
        lat,long=re.findall(r'"lat":(-?[\d\.]+),"lng":(-?[\d\.]+),"menuLandingPageUrl":null,"name":"'+loc.strip(),str(soup))[0]
        print(lat,long,loc)
        all.append([
            "https://www.miranchitorestaurants.com/",
            loc,    #name
            jso['address']['streetAddress'],
            jso['address']['addressLocality'],
            jso['address']['addressRegion'],
            jso['address']['postalCode'],
            'US',
            "<MISSING>",  # store #
            jso['address']['telephone'],  # phone
            jso['@type'],  # type
            lat,  # lat
            long,  # long
            tim,  # timing
            "https://www.miranchitorestaurants.com/"+loc.strip().lower().replace(' ','-')])
    return all

def scrape():
    data = fetch_data()
    write_output(data)


scrape()
