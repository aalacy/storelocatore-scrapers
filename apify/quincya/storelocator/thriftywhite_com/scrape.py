import csv
import json
from sgrequests import SgRequests
from bs4 import BeautifulSoup

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():

    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
    HEADERS = {'User-Agent' : user_agent}

    base_link = "https://thriftywhite.com/locations/"

    session = SgRequests()
    req = session.get(base_link, headers = HEADERS)
    base = BeautifulSoup(req.text,"lxml")

    all_scripts = base.find_all('script')
    for script in all_scripts:
        if "var locations" in str(script):
            script = str(script)
            break

    js = script.split("locations =")[1].split(";</scr")[0]
    stores = json.loads(js)

    data = []
    locator_domain = "thriftywhite.com"

    for store in stores:
        location_name = store["NAME"]
        street_address = (store["ADDRESS1"] + " " + store["ADDRESS2"]).strip()
        street_address = street_address.replace("Super One Foods","").replace("Leevers Foods","").replace("Plaza Shopping Center","").replace("Hugos","").replace("  ","").strip()
        city = store['CITY']
        state = store["STATE"]
        zip_code = store["ZIP"]
        country_code = "US"
        store_number = store["STORENUMBER"]
        location_type = "<MISSING>"
        phone = store['PHONE']
        hours_of_operation = ("Mon-Fri " + store["PHARM_HRS_M_F"] + " Sat " + store["PHARM_HRS_SAT"] + " Sun " + store["PHARM_HRS_SUN"]).strip()
        if "<br" in hours_of_operation:
            hours_of_operation = hours_of_operation.replace("Mon-Fri","").replace("<br>"," ").strip()
        latitude = store['XCOORD']
        longitude = store['YCOORD']
        link = "https://thriftywhite.com/store/" + store['STORELINK']

        # Store data
        data.append([locator_domain, link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])
    
    return data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
