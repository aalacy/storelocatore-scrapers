import csv
from sgrequests import SgRequests

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():

    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36'
    HEADERS = {'User-Agent' : user_agent}

    base_link = "https://api-triangle.partycity.ca/dss/services/v5/stores?lang=en&radius=1000&maxCount=100&includeServicesData=false&lat=44.6496062&lng=-63.6769585&storeType=store"

    session = SgRequests()
    stores = session.get(base_link, headers = HEADERS).json()

    data = []
    locator_domain = "partycity.ca"

    for store in stores:
        location_name = store["storeName"]
        street_address = store["storeAddress1"]
        city = store['storeCityName']
        state = store["storeProvince"]
        zip_code = store["storePostalCode"]
        country_code = "CA"
        store_number = store["storeNumber"]
        location_type = store['storeType'].replace("PTY","PARTY CITY").replace("CTR","CANADIAN TIRE")
        phone = store['storeTelephone']
        hours = store["workingHours"]['general']
        hours_of_operation = ("Monday " + hours["monOpenTime"] + "-" + hours["monCloseTime"] + " Tuesday " + hours["tueOpenTime"] + "-" + hours["tueCloseTime"] + " Wednesday " + hours["wedOpenTime"] + "-" + \
        hours["wedCloseTime"] + " Thursday " + hours["thuOpenTime"] + "-" + hours["thuCloseTime"] + " Friday " + hours["friOpenTime"] + "-" + hours["friCloseTime"] + " Saturday " + \
        hours["satOpenTime"] + "-" + hours["satCloseTime"] + " Sunday " + hours["sunOpenTime"] + "-" + hours["sunCloseTime"]).strip()
        latitude = store['storeLatitude']
        longitude = store['storeLongitude']
        if location_type == "PARTY CITY":
            link = "https://www.partycity.ca/en/store-details/%s/%s.store.html" %(state.lower(),store['storeCrxNodeName'])
        else:
            link = "<MISSING>"
        # Store data
        data.append([locator_domain, link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])
    
    return data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
