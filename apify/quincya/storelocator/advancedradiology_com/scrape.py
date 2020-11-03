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

    base_link = "https://www.advancedradiology.com/locator/search/json"

    session = SgRequests()
    payload = {'locator_division': '57',
                'locator_synopsys_name': 'Advanced Radiology'}
    stores = session.post(base_link,headers=HEADERS,data=payload).json()["matched"]

    data = []
    locator_domain = "advancedradiology.com"

    for store in stores:
        location_name = store["name"]
        street_address = store["address"].replace("\r\n"," ").split("(")[0].strip()
        city = store['city']
        state = store["state"]["abbreviation"]
        zip_code = store["postal"]
        country_code = "US"
        store_number = store["nid"]
        location_type = "<MISSING>"
        phone = store['numbers'][0]["number"]
        try:
            hours_of_operation = store["hours"]
            if not hours_of_operation:
                hours_of_operation = "<MISSING>"
        except:
            hours_of_operation = "<MISSING>"
        latitude = store['latitude']
        longitude = store['longitude']
        link = store['url']

        # Store data
        data.append([locator_domain, link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])
    
    return data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
