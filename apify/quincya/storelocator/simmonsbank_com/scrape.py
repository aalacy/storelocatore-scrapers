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

    base_link = 'https://www.simmonsbank.com/api/locations?radius=all'

    session = SgRequests()
    stores = session.get(base_link, headers = HEADERS).json()["locations"]

    data = []
    locator_domain = "simmonsbank.com"

    for store in stores:
        location_name = store["name"]
        try:
            street_address = (store["address"]["addressLine1"] + " " + store["address"]["addressLine2"]).strip()
        except:
            street_address = store["address"]["addressLine1"]
        city = store["address"]['city']
        state = store["address"]["state"]
        zip_code = store["address"]["zip"]
        country_code = "US"
        store_number = "<MISSING>"
        phone = store['phone']

        location_type = ""
        if store['fullService']:
            location_type = location_type + "Full Service"
        if store['atm']:
            location_type = location_type + ", ATM"
        if store['driveThru']:
            location_type = location_type + ", Drive-Thru"
        if location_type[:1] == ",":
            location_type = location_type[1:].strip()
        if not location_type:
            location_type = "<MISSING>"

        hours_of_operation = ""
        raw_hours = store["lobbyHours"]
        if "temporarily closed" in str(raw_hours):
            raw_hours = store["driveThruHours"]
        for day in raw_hours:
            if day == "overrideText":
                continue
            try:
                day_line = day.title() + " " + raw_hours[day]["open"] + "-" + raw_hours[day]["close"]
            except:
                day_line = day.title() + " Closed"
            hours_of_operation = (hours_of_operation + " " + day_line).strip()

        if location_type == "ATM":
            hours_of_operation = "Open 24 Hours"

        if hours_of_operation.count("Closed") == 7:
            if "temporarily closed" in str(store["lobbyHours"]):
                hours_of_operation = "Temporarily Closed"

        latitude = store['geocode']['latitude']
        longitude = store['geocode']['longitude']
        link = "<MISSING>"

        # Store data
        data.append([locator_domain, link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])
    
    return data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
