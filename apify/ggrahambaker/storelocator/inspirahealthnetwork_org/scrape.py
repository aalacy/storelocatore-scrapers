import csv
import json
from sgrequests import SgRequests
from bs4 import BeautifulSoup


def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    locator_domain = 'https://www.inspirahealthnetwork.org' 
    ext = '/locations/'

    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36'
    HEADERS = {'User-Agent' : user_agent}

    session = SgRequests()
    req = session.get(locator_domain + ext, headers = HEADERS)
    base = BeautifulSoup(req.text,"lxml")

    locs = base.find(class_="locations--results-wrap--list").find_all(role="article")

    link_list = []
    for loc in locs:
        link_tag = locator_domain + loc["about"]
        link_list.append(link_tag)

    all_store_data = []
    for link in link_list:
        r = session.get(link, headers=HEADERS)
        soup = BeautifulSoup(r.content, 'lxml')

        country_code = "US"
        
        info = soup.find('script', {'type': 'application/ld+json'}).text
        loc = json.loads(info)

        addy = loc['address']
        
        street_address = addy['streetAddress'].replace("\n"," ").strip()
        city = addy['addressLocality'].strip()
        state = addy['addressRegion'].strip()
        zip_code = addy['postalCode'].strip()
        
        try:
            phone_number = soup.find(class_="phone").a.text.strip()
        except:
            phone_number = '<MISSING>'

        coords = loc['geo']
        lat = coords['latitude']
        longit = coords['longitude']
        
        try:
            hours = loc['openingHours'].strip()
        except:
            hours = '<MISSING>'
        
        location_name = loc['name'].strip()
        store_number = '<MISSING>'
        try:
            location_type = ", ".join(list(soup.find(class_="related-services-items").stripped_strings))
        except:
            location_type = '<MISSING>'
        page_url = link

        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code, 
                    store_number, phone_number, location_type, lat, longit, hours, page_url]

        all_store_data.append(store_data)

    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
