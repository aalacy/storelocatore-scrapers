import csv
from sgrequests import SgRequests
import sgzip
from sgzip import DynamicZipSearch, SearchableCountries


def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():

    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36'
    HEADERS = {'User-Agent' : user_agent}

    session = SgRequests()

    MAX_RESULTS = 36
    MAX_DISTANCE = 20

    dup_tracker = []

    data = []
    locator_domain = "partycity.ca"

    search = sgzip.DynamicGeoSearch(country_codes=[SearchableCountries.CANADA],max_radius_miles=MAX_DISTANCE, max_search_results=MAX_RESULTS)

    search.initialize()

    coord = search.next()

    while coord:
        x = coord[0]
        y = coord[1]

        base_link = "https://api-triangle.partycity.ca/dss/services/v5/stores?lang=en&radius=%s&maxCount=%s&includeServicesData=false&lat=%s&lng=%s&storeType=store" %(MAX_DISTANCE,MAX_RESULTS,x,y)
        stores = session.get(base_link, headers = HEADERS).json()

        result_coords = []

        for store in stores:

            if "PTY" not in store['storeType']:
                continue

            store_number = store["storeNumber"]                        
            if store_number in dup_tracker:
                continue

            dup_tracker.append(store_number)
            latitude = store['storeLatitude']
            longitude = store['storeLongitude']
            
            result_coords.append([latitude,longitude])

            location_name = store["storeName"]
            street_address = store["storeAddress1"]
            city = store['storeCityName']
            state = store["storeProvince"]
            zip_code = store["storePostalCode"]
            country_code = "CA"
            location_type = '<MISSING>'
            phone = store['storeTelephone']
            hours = store["workingHours"]['general']
            hours_of_operation = ("Monday " + hours["monOpenTime"] + "-" + hours["monCloseTime"] + " Tuesday " + hours["tueOpenTime"] + "-" + hours["tueCloseTime"] + " Wednesday " + hours["wedOpenTime"] + "-" + \
            hours["wedCloseTime"] + " Thursday " + hours["thuOpenTime"] + "-" + hours["thuCloseTime"] + " Friday " + hours["friOpenTime"] + "-" + hours["friCloseTime"] + " Saturday " + \
            hours["satOpenTime"] + "-" + hours["satCloseTime"] + " Sunday " + hours["sunOpenTime"] + "-" + hours["sunCloseTime"]).strip()
            link = "https://www.partycity.ca/en/store-details/%s/%s.store.html" %(state.lower(),store['storeCrxNodeName'])
            # Store data
            data.append([locator_domain, link, location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])
                        
        if len(stores) > 0:
            search.update_with(result_coords)
        coord = search.next()

    return data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
