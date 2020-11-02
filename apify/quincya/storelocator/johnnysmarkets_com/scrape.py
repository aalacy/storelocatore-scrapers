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

    base_link = "https://johnnysmarkets.com/wp-admin/admin-ajax.php"

    session = SgRequests()

    # Request post
    payload = {'action': 'get_all_stores'}

    stores = session.post(base_link,headers=HEADERS,data=payload).json()

    data = []
    locator_domain = "johnnysmarkets.com"

    for store_num in stores:
        store = stores[store_num]
        location_name = "Johnny's - " + store["na"]
        street_address = store["st"]
        city = store['ct']
        state = store["rg"]
        zip_code = store["zp"]
        country_code = "US"
        store_number = store["ID"]
        location_type = "<MISSING>"
        phone = store['te']
        hours = store["de"].replace("\n", " ")
        if "Open 24" in hours:
            hours_of_operation = "Open 24 Hours"
        else:
            hours_of_operation = "<MISSING>"
        latitude = store['lat']
        longitude = store['lng']
        link = store["gu"]

        # Store data
        data.append([locator_domain, link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])
    
    return data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
