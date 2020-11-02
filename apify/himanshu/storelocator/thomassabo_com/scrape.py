import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import sgzip
from shapely.prepared import prep
from shapely.geometry import Point
from shapely.geometry import mapping, shape
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('thomassabo_com')





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


countries = {}


def getcountrygeo():
    data = session.get(
        "https://raw.githubusercontent.com/datasets/geo-countries/master/data/countries.geojson").json()

    for feature in data["features"]:
        geom = feature["geometry"]
        country = feature["properties"]["ADMIN"]
        countries[country] = prep(shape(geom))


def getplace(lat, lon):
    point = Point(float(lon), float(lat))
    for country, geom in countries.items():
        if geom.contains(point):
            return country

    return "unknown"


def fetch_data():
    getcountrygeo()
    return_main_object = []
    addresses = []
    search = sgzip.ClosestNSearch()
    search.initialize()
    MAX_RESULTS = 25
    MAX_DISTANCE = 70
    current_results_len = 0  # need to update with no of count.
    coord = search.next_coord()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
        # 'Content-type': 'application/x-www-form-urlencoded'
        "accept": "application/json, text/javascript, */*; q=0.01",
        "referer": "https://www.thomassabo.com/US/en_US/shopfinder",
        "x-requested-with": "XMLHttpRequest"


    }
    base_url = "https://www.thomassabo.com"
    while coord:
        result_coords = []
        # logger.info(coord)
        # ul="https://www.thomassabo.com/on/demandware.store/Sites-TS_US-Site/en_US/Shopfinder-GetStores?searchMode=radius&searchPhrase=&searchDistance=35&lat=40.7876&lng=-74.06&filterBy="
        f = "https://www.thomassabo.com/on/demandware.store/Sites-TS_US-Site/en_US/Shopfinder-GetStores?searchMode=radius&searchPhrase=&searchDistance=" + \
            str(MAX_DISTANCE) + "&lat=" + \
            str(coord[0]) + "&lng=" + str(coord[1]) + "&filterBy="
        # ulr1 = "https://www.thomassabo.com/on/demandware.store/Sites-TS_US-Site/en_US/Shopfinder-GetStores?searchMode=radius&searchPhrase=&searchDistance="+str(MAX_DISTANCE)+"&lat="+str(coord[0])+"="+str(coord[1])+"&filterBy="
        try:
            r = session.get(f).json()
        except:
            continue

        # soup= BeautifulSoup(r.text,"lxml")
        # k = json.loads(soup)
        # logger.info(soup)
        # url ="https://www.thomassabo.com/on/demandware.store/Sites-TS_INT-Site/en/Shopfinder-GetStores?searchMode=radius"+str(MAX_DISTANCE)+"&searchPhrase=10009&searchDistance=50&lat="+str(coord[0])+"&lng="+str(coord[1])+"&filterBy="
        # try:
        #     r = session.get(ulr1).json()
        # except:
        #     continue

        current_results_len = len(r)
        for loc in r:

            if "address1" in loc:
                latitude = loc['latitude']
                longitude = loc['longitude']
                country_name = getplace(latitude, longitude)
                if country_name not in["United States of America", "Canada", "unknown"]:
                    continue
                if "United States of America" in country_name:
                    country_code = "US"
                elif "Canada" in country_name:
                    country_code = "CA"
                else:
                    continue
                #logger.info(country_code)
                name = loc['name'].strip()
                address = loc['address1'].strip()
                city = loc['city'].strip()
                try:
                    state = loc['stateCode']
                except:
                    state = "<MISSING>"
                if "postalCode" in loc:
                    ca_zip_list = re.findall(
                        r'[A-Z]{1}[0-9]{1}[A-Z]{1}\s*[0-9]{1}[A-Z]{1}[0-9]{1}', str(loc["postalCode"]))
                    us_zip_list = re.findall(re.compile(
                        r"\b[0-9]{5}(?:-[0-9]{4})?\b"), str(loc["postalCode"]))
                    if us_zip_list:
                        zipp = us_zip_list[0]
                    elif ca_zip_list:
                        zipp = ca_zip_list[0]
                    else:
                        continue
                else:
                    # logger.info(loc)
                    # logger.info("~~~~~~~~~~~~~~~~~~~~~~~~~~~")

                    zipp = "<MISSING>"
                # logger.info(zipp, country_code)
                try:
                    hours = BeautifulSoup(loc["storeHours"], "lxml")
                    list_hours = list(hours.stripped_strings)
                    hour = " ".join(list_hours).strip()
                    # logger.info(hour)
                except:
                    hour = "<MISSING>"

                phone = ''
                if "phone" in loc:
                    phone = loc['phone'].strip()

                storeno = loc['ID'].strip()
                store = []

                result_coords.append((latitude, longitude))
                store.append(base_url)
                store.append(name if name else "<MISSING>")
                store.append(address if address else "<MISSING>")
                store.append(city if city else "<MISSING>")
                store.append(state if state else "<MISSING>")
                store.append(zipp if zipp else "<MISSING>")
                store.append(country_code if country_code else "<MISSING>")
                store.append(storeno if storeno else "<MISSING>")
                store.append(phone if phone else "<MISSING>")
                store.append("<MISSING>")
                store.append(latitude if latitude else "<MISSING>")
                store.append(longitude if longitude else "<MISSING>")
                store.append(hour if hour.strip() else "<MISSING>")
                store.append("<MISSING>")
                if store[2] in addresses:
                    continue
                addresses.append(store[2])
                yield store
                # logger.info("data====" + str(store))
                # logger.info(
                #     "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~`")

        if current_results_len < MAX_RESULTS:
            # logger.info("max distance update")
            search.max_distance_update(MAX_DISTANCE)
        elif current_results_len == MAX_RESULTS:
            # logger.info("max count update")
            search.max_count_update(result_coords)
        else:
            raise Exception("expected at most " +
                            str(MAX_RESULTS) + " results")
        coord = search.next_coord()


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
