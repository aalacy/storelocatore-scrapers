from sgrequests import SgRequests
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
    base_link = 'https://www.brookdale.com/bin/brookdale/search/global?fq=(contentCategory%3Alocations)&pt=31.9685988%2C-99.9018131&d=10000&rows=5000'

    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36'
    HEADERS = {'User-Agent' : user_agent}

    session = SgRequests()
    stores = session.get(base_link, headers = HEADERS).json()['locations']

    data = []
    locator_domain = 'brookdale.com'
    for store in stores:
        href = store.get('website')
        if href:
            location_name = store['name'].encode("ascii", "replace").decode().replace("?","")
            try:
                street_address = store['address1'] + " " + store['address2']
            except:
                street_address = store['address1'].strip()
            street_address = street_address.encode("ascii", "replace").decode().replace("?","")
            city = store['city']
            state = store['state']
            zip_code = store['zip_postal_code'][:5]
            country_code = "US"
            store_number = "<MISSING>"
            # phone = store['phone_main']
            phone = "<INACCESSIBLE>"
            location_type = "<MISSING>"
            hours_of_operation = "<MISSING>"
            latitude = store['latitude']
            longitude = store['longitude']

            data.append([locator_domain, href, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])
    return data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
