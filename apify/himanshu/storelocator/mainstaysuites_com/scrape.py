import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import sgzip
import datetime

def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
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
    coords = sgzip.coords_for_radius(100)
    return_main_object = []
    addresses = []

    for coord in coords:
        #print(coord[0], coord[1])
        url = "https://www.choicehotels.com/webapi/location/hotels"

        querystring = {"adults": "1", "checkInDate": "" + today + "", "checkOutDate": "" + tomorrow + "", "hotelSortOrder": "RELEVANCE", "include": "amenity_groups%2C%20amenity_totals%2C%20rating%2C%20relative_media", "lat": "" + str(coord[0]) + "", "lon": "" + str(
            coord[1]) + "", "minors": "0", "optimizeResponse": "image_url", "placeId": "", "placeName": "", "placeType": "PostalArea", "platformType": "DESKTOP", "preferredLocaleCode": "en-gb", "ratePlanCode": "RACK", "ratePlans": "RACK%2CPREPD%2CPROMO%2CFENCD", "rateType": "LOW_ALL", "rooms": "1", "searchRadius": "25", "siteName": "uk", "siteOpRelevanceSortMethod": "ALGORITHM_B"}

        payload = "------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"adults\"\r\n\r\n1\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"checkInDate\"\r\n\r\n" + today + "\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"checkOutDate\"\r\n\r\n" + tomorrow + \
            "\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"hotelSortOrder\"\r\n\r\nRELEVANCE\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"include\"\r\n\r\namenity_groups, amenity_totals, rating, relative_media\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"lat\"\r\n\r\n" + str(coord[0]) + "\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"lon\"\r\n\r\n" + str(
                coord[1]) + "\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"minors\"\r\n\r\n0\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"optimizeResponse\"\r\n\r\nimage_url\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"placeId\"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"placeName\"\r\n\r\n\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"placeType\"\r\n\r\nPostalArea\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"platformType\"\r\n\r\nDESKTOP\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"preferredLocaleCode\"\r\n\r\nen-gb\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"ratePlanCode\"\r\n\r\nRACK\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"ratePlans\"\r\n\r\nRACK,PREPD,PROMO,FENCD\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"rateType\"\r\n\r\nLOW_ALL\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW--"
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

        if "hotels" not in r.json():
            continue
        data = r.json()["hotels"]
        for store_data in data:
            if store_data["address"]["country"] != "US":
                continue
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
            store.append("<MISSING>")
            yield store

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
