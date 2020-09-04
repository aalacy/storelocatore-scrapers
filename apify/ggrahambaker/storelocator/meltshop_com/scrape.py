from sgrequests import SgRequests
from bs4 import BeautifulSoup
import csv

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():

    base_link = "https://www.meltshop.com/locations"

    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
    HEADERS = {'User-Agent' : user_agent}

    session = SgRequests()
    req = session.get(base_link, headers = HEADERS)
    base = BeautifulSoup(req.text,"lxml")

    locs = base.find_all(class_="summary-item")
    all_store_data = []

    locator_domain = 'meltshop.com/'

    for i, loc in enumerate(locs):
        ps = loc.find(class_='summary-excerpt').find_all('p')
        location_name = loc.find(class_='summary-title').text.strip()
        hours = ps[0].text.replace('\n', ' ')

        link = loc.find_all("a")[-1]["href"]
        # print(link)
        if "pittsburgh-airport" in link:
            link = "https://www.meltshop.com/locations/pittsburgh-airport"
            street_address = "1000 Airpot Blvd"
            city = "PITTSBURGH"
            state = "PA"
            zip_code = "15231"
            phone_number = '<MISSING>'
            country_code = 'US'
            location_type = '<MISSING>'
            lat = '<MISSING>'
            longit = '<MISSING>'
            store_number = '<MISSING>'
        else:
            req = session.get(link, headers = HEADERS)
            base = BeautifulSoup(req.text,"lxml")
                
            street_address = base.find(class_="street-address").text.replace("2829","2820").strip()
            city = base.find(class_="locality").text.strip()
            state = base.find(class_="region").text.strip()
            zip_code = base.find(class_="postal-code").text.strip()
            phone_number = base.find(class_="tel").text.strip()
            country_code = 'US'
            location_type = '<MISSING>'
            lat = base.find(class_="latitude").span["title"]
            longit = base.find(class_="longitude").span["title"]
            store_number = '<MISSING>'

        store_data = [locator_domain, link, location_name, street_address, city, state, zip_code, country_code,
                      store_number, phone_number, location_type, lat, longit, hours]
        all_store_data.append(store_data)
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
