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

    base_link = "https://demeter.bgood.com/api/website/v1/locations"

    session = SgRequests()
    states = session.get(base_link, headers = HEADERS).json()['locations']['North America']

    data = []
    locator_domain = "bgood.com"

    for state_name in states:
        stores = states[state_name]
        for store in stores:
            location_name = store["name"]
            street_address = store["address1"]
            city = store['city']
            state = store["state_code"]
            zip_code = store["zip_code"]
            country_code = store["country"]
            store_number = store["id"]
            location_type = "<MISSING>"
            phone = store['phone']
            if not phone:
                phone = "<MISSING>"
            hours_of_operation = ""
            try:
                raw_hours = store["schedules"]
                for raw_hour in raw_hours:
                    if not raw_hour["hours"]:
                        day_hours = "Closed"
                    else:
                        day_hours = raw_hour["hours"][0]["open"] + "-" + raw_hour["hours"][0]["close"]
                    hours_of_operation = (hours_of_operation + " " + raw_hour["day"] + " " + day_hours).strip()
            except:
                hours_of_operation = "Mon-Sun Closed"

            latitude = store['latitude']
            longitude = store['longitude']
            link = "https://www.bgood.com/locations/" + state_name.lower().replace(" ","-")

            # Store data
            data.append([locator_domain, link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])
    
    return data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
