import csv
from sgrequests import SgRequests
import json
import sgzip
import time
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('scppool_com')


session = SgRequests()


def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    search = sgzip.ClosestNSearch()
    search.initialize(country_codes=['US'])
    zip_code = search.next_zip()
    current_results_len = 0
    adressess = []
    base_url = "http://scppool.com"
    headers = {
        'accept': 'text/javascript, application/javascript, application/ecmascript, application/x-ecmascript, */*; q=0.01',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.9',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36',
    }
    while zip_code:
        result_coords = []
        # logger.info(f"zip code: {zip_code}")
        # logger.info("remaining zipcodes: " + str(search.zipcodes_remaining()))
        try:
            json_data = session.get(
                "http://scppool.com/map_api/?z="+str(zip_code), headers=headers).json()
        except Exception as ex:
            logger.info(f'Exception getting {zip_code}', ex)
            continue

        for store in json_data['locations']:
            location_name = store['sitename']+' '+store['sitenumber']
            street_address = store['address1']
            city = store['city'].replace(
                "Vereda La Isla, Cundinamarca", "Vereda La Isla")
            state = store['state'].replace("--", 'Cundinamarca')
            zipp = store['zip']
            phone = ''
            if "phone" in store:
                phone = store['phone']
            lat = store['latlon'].split(",")[0]
            lng = store['latlon'].split(",")[1]
            store_number = store['sitenumber']
            # logger.info(f'store number: {store_number}')
            page_url = "<MISSING>"
            hours = "<MISSING>"
            result_coords.append((lat, lng))
            store = []
            store.append(base_url)
            store.append(location_name)
            store.append(street_address)
            store.append(city)
            store.append(state)
            store.append(zipp)
            store.append("US")
            store.append(store_number)
            store.append(phone)
            store.append("<MISSING>")
            store.append(lat)
            store.append(lng)
            store.append(hours if hours else "<MISSING>")
            store.append(page_url)
            if store[2] in adressess:
                # logger.info(f'>>> already have store at {store[2]} <<<')
                continue
            adressess.append(store[2])
            store = [str(x).encode('ascii', 'ignore').decode(
                'ascii').strip() if x else "<MISSING>" for x in store]
            if "KM 7.5 Autopista a Medellin" in store:
                pass
            else:
                yield store
            # logger.info(store)

        search.max_count_update(result_coords)
        zip_code = search.next_zip()


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
