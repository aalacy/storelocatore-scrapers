import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import http.client
import sgzip
import json
import  pprint
import time
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('tropicalsmoothiecafe_com')




session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def request_wrapper(url,method,headers,data=None):
    request_counter = 0
    if method == "get":
        while True:
            try:
                r = session.get(url,headers=headers)
                return r
                break
            except:
                time.sleep(1)
                request_counter = request_counter + 1
                if request_counter > 10:
                    return None
                    break
    elif method == "post":
        while True:
            try:
                if data:
                    r = session.post(url,headers=headers,data=data)
                else:
                    r = session.post(url,headers=headers)
                return r
                break
            except:
                time.sleep(1)
                request_counter = request_counter + 1
                if request_counter > 10:
                    return None
                    break
    else:
        return None

def fetch_data():
    address = []
    base_url = "https://locations.tropicalsmoothiecafe.com"
    addresses = []
    search = sgzip.ClosestNSearch()
    search.initialize()
    MAX_RESULTS = 50
    MAX_DISTANCE = 100
    coords = search.next_coord()
    current_results_len = 0

    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36',
        'method': 'GET',
        'accept': 'application/json',
        'accept-encoding': 'gzip, deflate, br',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
    }
    

    while coords:

            result_coords = []
           # logger.info("zip_code === " + str(coords))
            #logger.info("ramiang zip =====" + str(search.current_zip))
            
            r = request_wrapper("https://locations.tropicalsmoothiecafe.com/search?q=" + str(search.current_zip) + "&r=" + str(MAX_RESULTS),'get', headers=headers)
            if r == None:
                search.max_distance_update(MAX_DISTANCE)
                coords = search.next_zip()
                continue
            soup = BeautifulSoup(r.text, "lxml")
            current_results_len =len(soup.find_all("span",{"class":re.compile("LocationName-brand")}))
            #logger.info(current_results_len)


            json = r.json()
            locations = json["locations"]

            for locations in locations:
                locator_domain = base_url
                loc = locations["loc"]
                cafe = loc["customByName"]
                location_name = cafe["Cafe Name for Reporting"]
                street_address = loc["address1"] + loc["address2"]
                city = loc["city"]
                state = loc["state"]
                zip = loc["postalCode"]
                store_number = loc["corporateCode"]
                country_code = loc["country"]
                phone = loc["phone"]
                location_type = " "
                latitude = loc["routableLatitude"]
                longitude = loc["routableLongitude"]
                result_coords.append((latitude, longitude))
                

                urls = loc["urls"]
                external = urls["external"]
                page_url = external["url"]
                
                hours = loc["hours"]
                days = hours["days"]

                jk = []
                hours_of_operation = ''
                for days in days:
                    day = days["day"]
                    intervals = days["intervals"]

                    for intervals in intervals:
                        start = str(intervals["start"]//100)
                        end = str((intervals["end"]//100)-12)
                    jk.append(day + ":" + start +  "AM" +"-"+ end + "PM ")

                hours_of_operation = ' '.join(jk)
            

                store = []
                store.append(locator_domain if locator_domain else '<MISSING>')
                store.append(location_name if location_name else '<MISSING>')
                store.append(street_address if street_address else '<MISSING>')
                store.append(city if city else '<MISSING>')
                store.append(state if state else '<MISSING>')
                store.append(zip if zip else '<MISSING>')
                store.append(country_code if country_code else '<MISSING>')
                store.append(store_number if store_number else '<MISSING>')
                store.append(phone if phone else '<MISSING>')
                store.append(location_type if location_type else '<MISSING>')
                store.append(latitude if latitude else '<MISSING>')
                store.append(longitude if longitude else '<MISSING>')
                store.append(hours_of_operation if hours_of_operation else '<MISSING>')
                store.append(page_url if page_url else '<MISSING>')
                if store[2] in address:
                    continue
                address.append(store[2])
                yield store

            if current_results_len < MAX_RESULTS:
                search.max_count_update(result_coords)
            else:
                raise Exception("expected at most " + str(MAX_RESULTS) + " results")

            coords = search.next_zip()

def scrape():
    data = fetch_data()
    write_output(data)

scrape()


