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

    MAX_RESULTS = 50
    MAX_DISTANCE = 15

    dup_tracker = []

    data = []
    locator_domain = "scotiabank.com"

    search = sgzip.DynamicGeoSearch(country_codes=[SearchableCountries.CANADA],max_radius_miles=MAX_DISTANCE,max_search_results=MAX_RESULTS)
    
    search.initialize()
    
    coord = search.next()

    while coord:
        x = coord[0]
        y = coord[1]

        base_link = "https://mapsms.scotiabank.com/branches?1=1&latitude=%s&longitude=%s&recordlimit=%s&locationtypes=1" %(x,y,MAX_RESULTS)
        try:
            stores = session.get(base_link, headers = HEADERS).json()['branchInfo']['marker']
        except:
            coord = search.next()
            continue

        result_coords = []

        for store in stores:
            store_number = store['@attributes']['id']
            if store_number in dup_tracker:
                continue
            dup_tracker.append(store_number)

            location_name = store['name']
            location_type = '<MISSING>'
            street_address = " ".join(store['address'].split(',')[:-3])
            city = store['address'].split(',')[-3].strip()
            if len(store['address'].split(',')[-2].split()) > 1:
                state = store['address'].split(',')[-2].strip()[:-7].strip()
                zip_code = store['address'].split(',')[-2].strip()[-7:].strip()
            else:
                state = store['address'].split(',')[-2].strip()
                zip_code = '<MISSING>'
            country_code = 'CA'
            phone = store['phoneNo']
            if not phone:
                phone = '<MISSING>'

            hours = store['hours']
            hours_of_operation = ""
            for day in hours:
                try:
                    day_hr = hours[day]["open"] + "-" + hours[day]["close"]
                except:
                    day_hr = "Closed"
                hours_of_operation = (hours_of_operation + " " + day + " " + day_hr).strip()
            if not hours_of_operation:
                hours_of_operation = '<MISSING>'
            
            latitude = store['@attributes']['lat']
            longitude = store['@attributes']['lng']

            # Store data
            data.append([locator_domain, '<MISSING>', location_name, street_address, city, state, zip_code, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation])
                        
        if len(stores) > 0:
            search.update_with(result_coords)
        coord = search.next()

    return data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
