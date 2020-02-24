import csv
import requests
from bs4 import BeautifulSoup
import re
import unicodedata
import sgzip

def write_output(data):
    with open('data.csv', mode='w',encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    main_url = "https://www.valueplace.com"
    return_main_object = []
    addresses = []
    search = sgzip.ClosestNSearch()
    search.initialize(include_canadian_fsas=True)
    MAX_RESULTS = 200
    MAX_DISTANCE = 150
    coord = search.next_coord()
    while coord:
        result_coords = []
        #print("remaining zipcodes: " + str(len(search.zipcodes)))
        x = coord[0]
        y = coord[1]
        #print('Pulling Lat-Long %s,%s...' % (str(x), str(y)))
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36',
        }
        r = requests.get("https://www-api.woodspring.com/v1/gateway/hotel/hotels?lat=" + str(x) + "&lng=" + str(y) + "&max=200&offset=0&radius=150",headers=headers)
        if "searchResults" not in r.json():
            search.max_distance_update(MAX_DISTANCE)
            coord = search.next_coord()
            continue
        data = r.json()["searchResults"]
        for store_data in data:
            result_coords.append((store_data["geographicLocation"]["latitude"], store_data["geographicLocation"]["longitude"]))
            if store_data["address"]["countryCode"] != "US" and store_data["address"]["countryCode"] != "CA":
                continue
            store = []
            store.append(main_url)
            store.append(store_data["hotelName"])
            location_request = requests.get("https://www-api.woodspring.com/v1/gateway/hotel/hotels/" + str(store_data["hotelId"]) + "?include=location,phones",headers=headers)
            location_data = location_request.json()
            if location_data["hotelInfo"]["hotelSummary"]['hotelStatus'] == "Closed":
                continue
            add = location_data["hotelInfo"]["hotelSummary"]["addresses"][0]
            store.append(",".join(add["street"]))
            if store[-1] in addresses:
                continue
            addresses.append(store[-1])
            store.append(add["cityName"] if add["cityName"] else "<MISSING>")
            if "," + store[-1] + "," in store[2]:
                store[2] = store[2].split("," + store[-1])[0]
            store.append(add["subdivisionCode"] if add["subdivisionCode"] else "<MISSING>")
            store.append(add["postalCode"] if add["postalCode"] else "<MISSING>")
            store.append(add["countryCode"])
            store.append("<MISSING>")
            try:
                store.append(location_data["hotelInfo"]["hotelSummary"]["phones"][1]["areaCode"] + location_data["hotelInfo"]["hotelSummary"]["phones"][1]["number"] if location_data["hotelInfo"]["hotelSummary"]["phones"] else "<MISSING>")
            except:
                store.append(location_data["hotelInfo"]["hotelSummary"]["phones"][-1]["number"] if location_data["hotelInfo"]["hotelSummary"]["phones"] and len(location_data["hotelInfo"]["hotelSummary"]["phones"][-1]["number"]) != 7 else "<MISSING>")
            store.append("<MISSING>")
            store.append(store_data["geographicLocation"]["latitude"])
            store.append(store_data["geographicLocation"]["longitude"])
            try:
                store.append(location_data['hotelInfo']['policyCodes'][0]['policyDescription'][0].replace("Hotel Office Hours :","").replace("|","").strip())
            except:
                store.append("<MISSING>")
            store.append("https://www.woodspring.com/" + str(store_data["hotelId"]))
            for i in range(len(store)):
                if type(store[i]) == str:
                    store[i] = ''.join((c for c in unicodedata.normalize('NFD', store[i]) if unicodedata.category(c) != 'Mn'))
            store = [x.replace("–","-") if type(x) == str else x for x in store]
            store = [x.encode('ascii', 'ignore').decode('ascii').strip() if type(x) == str else x for x in store]
            yield store
        if len(data) < MAX_RESULTS:
            #print("max distance update")
            search.max_distance_update(MAX_DISTANCE)
        elif len(data) == MAX_RESULTS:
            #print("max count update")
            search.max_count_update(result_coords)
        else:
            raise Exception("expected at most " + str(MAX_RESULTS) + " results")
        coord = search.next_coord()

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
