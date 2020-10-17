import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def parse_addy(addy):
    arr = addy.split(',')
    if len(arr) == 4:
        arr = [" ".join(arr[:2]).replace("  "," "), arr[2], arr[3]]
    street_address = arr[0].strip()
    city = arr[1].strip()
    state_zip = arr[2].strip().split(' ')
    state = state_zip[0]
    zip_code = state_zip[1]
    
    return street_address, city, state, zip_code

def fetch_data():

    locator_domain = 'https://primary-health.net/' 
    ext = 'Locations.aspx'

    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
    HEADERS = {'User-Agent' : user_agent}

    session = SgRequests()

    req = session.get(locator_domain + ext, headers = HEADERS)
    base = BeautifulSoup(req.text,"lxml")

    hrefs = base.find_all('a', {'href': re.compile(r'LocationDetail\.aspx\?id=.+')})
    links = [locator_domain + h['href'] for h in hrefs]

    all_store_data = []
    for link in links:
        req = session.get(link, headers = HEADERS)
        base = BeautifulSoup(req.text,"lxml")
        
        main = base.find(class_='page-title')
        
        location_name = main.h1.text.encode("ascii", "replace").decode().replace("?","'").strip()
        
        hours = base.find('span', attrs={'itemprop': "openingHours"}).text.encode("ascii", "replace").decode().replace("?","-").replace('\n', ' ')\
        .replace('pm', 'pm ').replace('PM', 'PM ').replace('Closed', 'Closed ').split('Dental')[0].strip()
        if hours == '':
            hours = '<MISSING>'
        if "temporarily closed" in hours:
            hours = "Temporarily Closed"
        if "Visit Site" in hours:
            hours = '<MISSING>'
        
        phone_number = main.find(id='PageTitle_SiteList2_PhoneLabel_0').text.strip()
        
        addy = main.find(id='PageTitle_SiteList2_AddressLabel_0').text.replace("Blvd. Yea","Blvd, Yea").replace("  "," ").strip()
        street_address, city, state, zip_code = parse_addy(addy)

        country_code = 'US'
        store_number = link.split("=")[-1]
        location_type = '<MISSING>'

        geo = base.find('meta', attrs={'name': "keywords"})['content'].split(",")
        lat = geo[1].replace("lat","").strip()
        longit = geo[0].replace("long","").strip()

        if "-" in lat:
            lat = geo[0].replace("lat","").strip()
            longit = geo[1].replace("long","").strip()

        page_url = link

        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code, 
                    store_number, phone_number, location_type, lat, longit, hours, page_url]

        all_store_data.append(store_data)

    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
