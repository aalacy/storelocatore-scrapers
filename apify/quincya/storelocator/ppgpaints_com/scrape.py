import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import sgzip
from sgzip import DynamicGeoSearch, SearchableCountries

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    session = SgRequests()
    HEADERS = { 'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36' }
    locator_domain = 'ppgpaints.com'

    all_store_data = []

    dup_tracker = []

    search = sgzip.DynamicZipSearch(country_codes=[SearchableCountries.USA])

    search.initialize()
    postcode = search.next()

    while postcode:

        base_link = 'https://www.ppgpaints.com/store-locator/search?value=%s&filter=Store' %postcode
        stores = session.post(base_link,headers=HEADERS).json()["Items"]

        result_coords = []

        for loc in stores:
            page_url = "https://www.ppgpaints.com" + loc['LocationUrl']
            if page_url in dup_tracker:
                continue
            dup_tracker.append(page_url)

            lat = loc['Latitude']
            longit = loc['Longitude']
            result_coords.append([lat, longit])
            search.update_with(result_coords)

            location_name = loc['Name']
            street_address = (loc['Street1'] + " " + loc['Street2'] + " " + loc['Street3'] + " " + loc['Street4']).strip()
            city = loc['City']
            state = loc['State']
            if state == "VI":
            	continue
            zip_code = loc['PostalCode']
            country_code = "US"
            store_number = location_name.split()[-1]
            if not store_number.isdigit():
            	store_number = '<MISSING>'
            phone_number = loc['PhoneNumber']
            location_type = '<MISSING>'

            if "temporarily closed" in location_name.lower():
                hours = "Temporarily Closed"
                store_number = '<MISSING>'
            else:
                req = session.get(page_url, headers = HEADERS)
                base = BeautifulSoup(req.text,"lxml")
                try:
                    hours = " ".join(list(base.find(class_="hours-dropdown").stripped_strings))
                except:
                    hours = '<MISSING>'
                hours = '<INACCESSIBLE>'
            
            store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code, 
                        store_number, phone_number, location_type, lat, longit, hours, page_url]

            all_store_data.append(store_data)

        postcode = search.next()

    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
