import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import unicodedata
import sgzip
from shapely.prepared import prep
from shapely.geometry import Point
from shapely.geometry import mapping, shape


session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

countries = {}

def getcountrygeo():
   data = session.get("https://raw.githubusercontent.com/datasets/geo-countries/master/data/countries.geojson").json()
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
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    return_main_object = []
    addresses = []
    search = sgzip.ClosestNSearch()
    search.initialize()
    MAX_RESULTS = 20
    coord = search.next_coord()
    while coord:
        result_coords = []
        #print("remaining zipcodes: " + str(search.zipcodes_remaining()))
        x = coord[0]
        y = coord[1]
        #print('Pulling Lat-Long %s,%s...' % (str(x), str(y)))
        r = session.get("https://global.tommy.com/en_int/api/store_finder?lat="+ str(x) + "&lng=" + str(y) + "&radius=50000000",headers=headers)
        data = r.json()["data"]
        for store_data in data:
            country = store_data["title"].split(",")[0]
            if "US" not in country and "CA" not in country:
                continue
            lat = store_data["lat"]
            lng = store_data["lng"]
            result_coords.append((lat, lng))
            country_name = getplace(lat, lng)
            if "United States of America" != country_name and "Canada" != country_name:
                continue
            store = []
            location_soup = BeautifulSoup(store_data["html"]["store_block"],"lxml")
            name = location_soup.find("h3").text.strip()
            phone_split = re.findall(re.compile(".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"),store_data["html"]["store_block"])
            if phone_split:
                phone = phone_split[0]
            else:
                phone = "<MISSING>"
            hours = " ".join(list(location_soup.find("div",{"class":'store-openinghours'}).stripped_strings))
            store.append("https://global.tommy.com")
            store.append("<MISSING>")
            store.append(",".join(store_data["title"].split(",")[1:-2]).strip().replace("\n",""))
            if store[-1] in addresses:
                continue
            addresses.append(store[-1])
            store.append(store_data["title"].split(",")[-2])
            store.append(store_data["title"].split(",")[-1])
            store.append("<MISSING>")
            store.append("US" if country_name == "United States of America" else "CA")
            store.append(store_data["id"])
            store.append(phone if phone and "," not in phone else "<MISSING>")
            store.append("<MISSING>")
            store.append(lat)
            store.append(lng)
            store.append(hours if hours and hours != "Opening hours" else "<MISSING>")
            store.append("<MISSING>")
            for i in range(len(store)):
                if type(store[i]) == str:
                    store[i] = ''.join((c for c in unicodedata.normalize('NFD', store[i]) if unicodedata.category(c) != 'Mn'))
            yield store
        if len(data) == MAX_RESULTS:
            #print("max count update")
            search.max_count_update(result_coords)
        else:
            raise Exception("expected at most " + str(MAX_RESULTS) + " results")
        coord = search.next_coord()

def scrape():
    data = fetch_data()
    write_output(data)


scrape()
