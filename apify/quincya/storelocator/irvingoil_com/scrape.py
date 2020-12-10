import csv
from sgrequests import SgRequests

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():

    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
    HEADERS = {'User-Agent' : user_agent}

    base_link = "https://www.irvingoil.com/location/geojson/"

    session = SgRequests()
    stores = session.get(base_link, headers = HEADERS).json()["features"]

    data = []
    found_poi = []
    locator_domain = "irvingoil.com"

    for store in stores:
        store = store['properties']
        location_name = store["name"]
        raw_address = store["address"].split("<br/>")
        street_address = raw_address[0].replace("\r\n"," ").replace("amp;","").strip()
        city = raw_address[1].split(",")[0]

        if street_address+city in found_poi:
            continue
        found_poi.append(street_address+city)

        zip_code = raw_address[1].split(",")[1].split()[-1]
        if len(zip_code) < 4:
            zip_code = " ".join(raw_address[1].split(",")[1].split()[-2:])
            country_code = "CA"
        elif len(zip_code) > 5:
            country_code = "CA"
        else:
            country_code = "US"

        state = raw_address[1].split(",")[1].replace(zip_code,"").strip()
        store_number = store["nid"]
        location_type = "<MISSING>"
        phone = store['phone']
        if not phone:
            phone = "<MISSING>"
        hours_of_operation = "<INACCESSIBLE>"
        latitude = store['lat']
        longitude = store['long']
        link = "https://www.irvingoil.com" + store['link']

        # Store data
        data.append([locator_domain, link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])
    
    return data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
