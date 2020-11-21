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

    base_link = "https://www.sunoco.com/js/locations.json"

    session = SgRequests()
    stores = session.get(base_link, headers = HEADERS).json()

    data = []
    found = []
    locator_domain = "sunoco.com"

    for store in stores:
        location_name = "SUNOCO #" + str(store["Facility ID"])
        if location_name in found:
            continue
        found.append(location_name)
        street_address = store["Address"].replace("  "," ")
        city = store['City']
        state = store["State"]
        zip_code = str(store["Zip"])
        if len(zip_code) < 5:
            zip_code = "0" + zip_code
        if len(zip_code) < 4:
            zip_code = "<MISSING>"
        country_code = "US"
        store_number = store["Facility ID"]
        location_type = "<MISSING>"
        phone = store['Phone']
        if len(str(phone)) < 5:
            phone = "<MISSING>"
        hours_of_operation = ("Mon-Sat " + str(store["Hrs of Operation Mon-Sat Open"]) + "-" + str(store["Hrs of Operation Mon-Sat Close"]) + " Sun " + str(store["Hrs of Operation Sun Open"]) + "-" + str(store["Hrs of Operation Sun Close"])).strip()
        if hours_of_operation == "Mon-Sat 0-2400 Sun 0-2400" or hours_of_operation == "Mon-Sat 0-0 Sun 0-0":
            hours_of_operation = "Open 24 hours"
        latitude = store['Latitude']
        longitude = store['Longitude']
        if not latitude or latitude == "NULL":
            latitude = "<MISSING>"
            longitude = "<MISSING>"
        link = "<MISSING>"

        # Store data
        data.append([locator_domain, link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])
    
    return data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
