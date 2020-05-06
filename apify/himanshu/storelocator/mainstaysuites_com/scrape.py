import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import sgzip
import datetime

def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8",newline='') as output_file:
        writer = csv.writer(output_file, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    today = datetime.date.today().strftime("%Y-%m-%d")
    tomorrow = (datetime.date.today() +
                datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    search = sgzip.ClosestNSearch()
    search.initialize(country_codes= ["US"])
    MAX_RESULTS = 100
    MAX_DISTANCE = 25
    coords = search.next_coord()

    addresses = []

    while coords:
        result_coords = []
        # print("remaining zipcodes: " + str(len(search.zipcodes)))
        #print(coord[0], coord[1])
        url = "https://www.choicehotels.com/webapi/location/hotels"

        querystring = {"adults": "1", "checkInDate": "" + today + "", "checkOutDate": "" + tomorrow + "", "hotelSortOrder": "RELEVANCE", "include": "amenity_groups%2C%20amenity_totals%2C%20rating%2C%20relative_media", "lat": "" + str(coords[0]) + "", "lon": "" + str(
            coords[1]) + "", "minors": "0", "optimizeResponse": "image_url", "placeId": "", "placeName": "", "placeType": "PostalArea", "platformType": "DESKTOP", "preferredLocaleCode": "en-us", "ratePlanCode": "RACK", "ratePlans": "RACK%2CPREPD%2CPROMO%2CFENCD", "rateType": "LOW_ALL", "rooms": "1", "searchRadius": "25", "siteName": "us", "siteOpRelevanceSortMethod": "ALGORITHM_B"}

        payload = "------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"adults\"\r\n\r\n1\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"checkInDate\"\r\n\r\n" + today + "\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"checkOutDate\"\r\n\r\n" + tomorrow + \
            "\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"hotelSortOrder\"\r\n\r\nRELEVANCE\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"include\"\r\n\r\namenity_groups, amenity_totals, rating, relative_media\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"lat\"\r\n\r\n" + str(coords[0]) + "\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"lon\"\r\n\r\n" + str(
                coords[1]) + "\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"minors\"\r\n\r\n0\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"optimizeResponse\"\r\n\r\nimage_url\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"placeId\"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"placeName\"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"placeType\"\r\n\r\nPostalArea\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"platformType\"\r\n\r\nDESKTOP\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"preferredLocaleCode\"\r\n\r\nen-us\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"ratePlanCode\"\r\n\r\nRACK\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"ratePlans\"\r\n\r\nRACK,PREPD,PROMO,FENCD\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"rateType\"\r\n\r\nLOW_ALL\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW--"
        headers = {
            'content-type': "multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW",
            'Content-type': "application/json, text/plain, */*",
            'Content-Type': "application/x-www-form-urlencoded; charset=UTF-8",
            'adrum': "isAjax:true",
            'User-Agent': "PostmanRuntime/7.20.1",
            'Accept': "*/*",
            'Cache-Control': "no-cache",
            'Postman-Token': "a44bbb18-e82f-440f-bf26-6ba8c9d1a708,aa969f54-b730-4594-950f-2ee209d39b34",
            'Host': "www.choicehotels.com",
            'Accept-Encoding': "gzip, deflate",

            'Content-Length': "2096",
            'Connection': "keep-alive",
            'cache-control': "no-cache"
        }
        brand = {"AC":"ascend-hotels","BR":"cambria-hotels","CL":"clarion-hotels","CI":"comfort-inn-hotels","CS":"comfort-suites-hotels","EL":"econo-lodge-hotels","MS":"mainstay-suites-hotels","QI":"quality-inn-hotels","RW":"rodeway-inn-hotels","SL":"sleep-inn-hotels","SB":"suburban-hotels","WS":"woodspring-hotels","FR":"choice-hotels"}
        session = SgRequests()
        r = session.post(url, data=payload, headers=headers, params=querystring)

        if "hotels"  in r.json():
        
            data = r.json()["hotels"]
            for store_data in data:
                if "US" in store_data["address"]["country"] :
                
                # print(store_data['brandName'],store_data['brandCode'])
                # print(store_data["address"]["postalCode"])
                    page_url = "https://www.choicehotels.com/"+str(store_data["address"]["subdivision"].lower())+"/"+str(store_data["address"]["city"].replace(" ","-").lower())+"/"+str(brand[store_data['brandCode']])+"/"+str(store_data["id"].lower())
                    result_coords.append((store_data["lat"],store_data["lon"]))
                    store = []
                    store.append("https://mainstaysuites.com")
                    store.append(store_data["name"])
                    address = ""
                    if "line1" in store_data["address"]:
                        address = address + store_data["address"]["line1"]
                    if "line2" in store_data["address"]:
                        address = address + store_data["address"]["line2"]
                    if "line3" in store_data["address"]:
                        address = address + store_data["address"]["line3"]
                    store.append(address)
                    if store[-1] in addresses:
                        continue
                    addresses.append(store[-1])
                    store.append(store_data["address"]["city"])
                    store.append(store_data["address"]["subdivision"])
                    store.append(store_data["address"]["postalCode"])
                    if len(store[-1]) == 10:
                        store[-1] = store[-1][:5] + "-" + store[-1][6:]
                    store.append(store_data["address"]["country"])
                    store.append(store_data["id"])
                    store.append(store_data["phone"])
                    store.append("<MISSING>")
                    store.append(store_data["lat"])
                    store.append(store_data["lon"])
                    store.append("<MISSING>")
                    store.append(page_url)
                    # print("data =="+str(store))
                    yield store

        if len(data) < MAX_RESULTS:
            # print("max distance update")
            search.max_distance_update(MAX_DISTANCE)
        elif len(data) == MAX_RESULTS:
            # print("max count update")
            search.max_count_update(result_coords)
        else:
            raise Exception("expected at most " + str(MAX_RESULTS) + " results")
        coords = search.next_coord()



    ### for CANADA location


    today = datetime.date.today().strftime("%Y-%m-%d")
    tomorrow = (datetime.date.today() +
                datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    search = sgzip.ClosestNSearch()
    search.initialize(country_codes= ["CA"])
    MAX_RESULTS = 100
    MAX_DISTANCE = 25
    coords = search.next_coord()

    return_main_object = []
    addresses1 = []

    while coords:
        # print("remaining zipcodes: " + str(len(search.zipcodes)))
        result_coords = []
        lat = coords[0]
        lng = coords[1]
        url = "https://www.choicehotels.com/webapi/location/hotels"

        querystring = {"adults": "1", "checkInDate": "" + today + "", "checkOutDate": "" + tomorrow + "", "hotelSortOrder": "RELEVANCE", "include": "amenity_groups%2C%20amenity_totals%2C%20rating%2C%20relative_media", "lat": "" + str(lat) + "", "lon": "" + str(
            lng) + "", "minors": "0", "optimizeResponse": "image_url", "placeId": "", "placeName": "", "placeType": "PostalArea", "platformType": "DESKTOP", "preferredLocaleCode": "en-ca", "ratePlanCode": "RACK", "ratePlans": "RACK%2CPREPD%2CPROMO%2CFENCD", "rateType": "LOW_ALL", "rooms": "1", "searchRadius": "25", "siteName": "ca", "siteOpRelevanceSortMethod": "ALGORITHM_B"}

        payload = "------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"adults\"\r\n\r\n1\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"checkInDate\"\r\n\r\n" + today + "\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"checkOutDate\"\r\n\r\n" + tomorrow + \
            "\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"hotelSortOrder\"\r\n\r\nRELEVANCE\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"include\"\r\n\r\namenity_groups, amenity_totals, rating, relative_media\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"lat\"\r\n\r\n" + str(lat) + "\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"lon\"\r\n\r\n" + str(
                lng) + "\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"minors\"\r\n\r\n0\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"optimizeResponse\"\r\n\r\nimage_url\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"placeId\"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"placeName\"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"placeType\"\r\n\r\nPostalArea\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"platformType\"\r\n\r\nDESKTOP\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"preferredLocaleCode\"\r\n\r\nen-ca\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"ratePlanCode\"\r\n\r\nRACK\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"ratePlans\"\r\n\r\nRACK,PREPD,PROMO,FENCD\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"rateType\"\r\n\r\nLOW_ALL\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW--"
        headers = {
            'content-type': "multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW",
            'Content-type': "application/json, text/plain, */*",
            'Content-Type': "application/x-www-form-urlencoded; charset=UTF-8",
            'adrum': "isAjax:true",
            'User-Agent': "PostmanRuntime/7.20.1",
            'Accept': "*/*",
            'Cache-Control': "no-cache",
            'Postman-Token': "a44bbb18-e82f-440f-bf26-6ba8c9d1a708,aa969f54-b730-4594-950f-2ee209d39b34",
            'Host': "www.choicehotels.com",
            'Accept-Encoding': "gzip, deflate",

            'Content-Length': "2096",
            'Connection': "keep-alive",
            'cache-control': "no-cache"
        }

        session = SgRequests()
        r = session.post(url, data=payload, headers=headers, params=querystring)

        if "hotels" in r.json():
        
            data = r.json()["hotels"]
            for store_data1 in data:
                result_coords.append((store_data1["lat"],store_data1["lon"]))
                store1 = []
                store1.append("https://mainstaysuites.com")
                page_url = "https://www.choicehotels.com/"+str(store_data["address"]["subdivision"].lower())+"/"+str(store_data["address"]["city"].replace(" ","-").lower())+"/"+str(brand[store_data['brandCode']])+"/"+str(store_data["id"].lower())
                store1.append(store_data1["name"])
                address = ""
                if "line1" in store_data1["address"]:
                    address = address + store_data1["address"]["line1"]
                if "line2" in store_data1["address"]:
                    address = address + store_data1["address"]["line2"]
                if "line3" in store_data1["address"]:
                    address = address + store_data1["address"]["line3"]
                store1.append(address)
                if store1[-1] in addresses1:
                    continue
                addresses1.append(store1[-1])
                store1.append(store_data1["address"]["city"])
                store1.append(store_data1["address"]["subdivision"])
                store1.append(store_data1["address"]["postalCode"])
                if len(store1[-1]) == 10:
                    store1[-1] = store1[-1][:5] + "-" + store1[-1][6:]
                store1.append(store_data1["address"]["country"])
                store1.append(store_data1["id"])
                store1.append(store_data1["phone"])
                store1.append("<MISSING>")
                store1.append(store_data1["lat"])
                store1.append(store_data1["lon"])
                store1.append("<MISSING>")
                store1.append(page_url)
                # print("data =="+str(store1))
                yield store1


        if len(data) < MAX_RESULTS:
            # print("max distance update")
            search.max_distance_update(MAX_DISTANCE)
        elif len(data) == MAX_RESULTS:
            # print("max count update")
            search.max_count_update(result_coords)
        else:
            raise Exception("expected at most " + str(MAX_RESULTS) + " results")
        coords = search.next_coord()
def scrape():
    data = fetch_data()
    write_output(data)

scrape()
