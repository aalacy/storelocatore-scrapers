import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():

    session = SgRequests()

    state_list = ["AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DC", "DE", "FL", "GA", 
          "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", 
          "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ", 
          "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC", 
          "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"]

    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
    HEADERS = {'User-Agent' : user_agent}

    data = []
    locator_domain = "johnstonesupply.com"

    for s in state_list:
        base_link = "https://johnstonesupply.com/rest/js-store/findByState?state=%s" %s.lower()
        stores = session.get(base_link, headers = HEADERS).json()

        for store in stores:
            location_name = store["description"]
            street_address = store["streetAddress"].strip()
            city = store['city']
            state = store["state"]
            zip_code = store["zipCode"]
            country_code = "US"
            store_number = store["storeNumber"]
            location_type = "<MISSING>"
            phone = store['phoneNumber'].split("<")[0].split(" (")[0].strip()
            hours_of_operation = "<MISSING>"
            latitude = "<MISSING>"
            longitude = "<MISSING>"
            link = "<MISSING>"

            # Store data
            data.append([locator_domain, link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])
    
    # Canada
    base_link = "https://johnstonesupply.com/"
    req = session.get(base_link, headers = HEADERS)
    base = BeautifulSoup(req.text,"lxml")

    items = base.find(id="modalFindStoreCanada").find_all(class_="row mb-3 border-bottom pb-3 modal-store-result")
    for item in items:
        location_name = item.p.text.strip()
        street_address = item.p.text.strip()
        city = item.find(class_="d-block").text.split(",")[0].strip()
        state = item.find(class_="d-block").text.split(",")[1].split()[0].strip()
        zip_code = item.find(class_="d-block").text[-8:].strip()
        country_code = "CA"
        store_number = item.find_all("a")[-1]["href"].split("tore")[1]
        location_type = "<MISSING>"
        phone = item.find_all("a")[-2].text
        hours_of_operation = "<MISSING>"
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
