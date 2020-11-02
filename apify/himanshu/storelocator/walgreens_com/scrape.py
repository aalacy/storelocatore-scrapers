import csv
import json
import sgzip
from sgrequests import SgRequests

session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8", newline="") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    keys = set()
    search = sgzip.ClosestNSearch()
    search.initialize()
    MAX_DISTANCE = 25
    zip_code = search.next_zip()
    base_url = "https://www.walgreens.com"
    while zip_code:
        result_coords = []
        url = "https://www.walgreens.com/locator/v1/stores/search?requestor=search"
        payload = "{\"r\":\"1000\",\"zip\":%s,\"requestType\":\"dotcom\",\"s\":\"1000\"}"%('"{}"'.format(str(zip_code)))
        headers = {
            'Content-Type': 'application/json'
        }
        r = session.post( url, headers=headers, data = payload).json()
        if "results" in r:
            locator_domain = base_url
            location_name = ""
            street_address = ""
            city = ""
            state = ""
            zipp = ""
            country_code = "US"
            store_number = ""
            phone = ""
            location_type = ""
            latitude = ""
            longitude = ""
            raw_address = ""
            hours_of_operation = ""
            for location in r["results"]:
                storeNumber = location['store']['storeNumber']
                location_name = "Walgreens - Store #"+str(storeNumber)
                phone =location['store']['phone']['areaCode'] + ' '+ location['store']['phone']['number']
                storeNumber = location['storeNumber']
                latitude = location['latitude']
                longitude = location['longitude']
                zipp = location['store']['address']['zip']
                if zipp.replace("-","").strip().isdigit():
                    country_code = "US"
                else:
                    country_code = "CA"
                if phone.strip().lstrip():
                    phone = phone
                else:
                    phone = "<MISSING>"  
                page_url = "https://www.walgreens.com"+location['storeSeoUrl']
                days = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']
                start = location['store']['storeOpenTime']
                end = location['store']['storeCloseTime']
                hours_of_operation = ', '.join(['{}: {}-{}'.format(day, start, end) for day in days])
                result_coords.append((latitude, longitude))
                store = [locator_domain, location_name, location['store']['address']['street'].capitalize(), location['store']['address']['city'].capitalize(), location['store']['address']['state'], zipp, country_code,
                        storeNumber, phone.strip(), location_type, latitude, longitude, hours_of_operation,page_url]

                if storeNumber in keys:
                    continue
                keys.add(storeNumber)
                store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
                yield store
        if len(result_coords) == 0:
            search.max_distance_update(MAX_DISTANCE)
        else:
            search.max_count_update(result_coords)
        zip_code = search.next_zip()
        
def scrape():
    data = fetch_data()
    write_output(data)
scrape()
