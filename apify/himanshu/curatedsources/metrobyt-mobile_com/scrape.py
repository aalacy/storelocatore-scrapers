import csv
from bs4 import BeautifulSoup
import re
import json
import sgzip
import ssl
from sglogging import SgLogSetup
from sgrequests import SgRequests
session = SgRequests()
logger = SgLogSetup().get_logger('metrobyt-mobile')



try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    #logger.info("Error##################")
    # Legacy Python that doesn't verify HTTPS certificates by default
    pass
else:
    # Handle target environment that doesn't support HTTPS verification
    ssl._create_default_https_context = _create_unverified_https_context


def write_output(data):
    with open('data.csv', mode='w', newline="") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","store_name","page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    addressess = []
    addresses1 =[]
    search = sgzip.ClosestNSearch()
    search.initialize()
    MAX_RESULTS = 100000
    MAX_DISTANCE = 10
    current_results_len = 0  # need to update with no of count.
    coord = search.next_coord()


    response1 =0
    while coord:
        # logger.info("remaining zipcodes: " + str(search.zipcodes_remaining()))
        result_coords = []
        lat = coord[0]
        lng = coord[1]
        base_url = "https://www.metrobyt-mobile.com/"
        url = "https://www.metrobyt-mobile.com/api/v1/commerce/store-locator"
        # logger.info(str(search.current_zip))
        # data="https://www.metrobyt-mobile.com/api/v1/commerce/store-locator?address=10429%20n%2019th%20ave%20phoenix%20az&store-type=All&min-latitude=33.58853657681159&max-latitude=33.58853657681159&min-longitude=-112.10864146226419&max-longitude=-112.10864146226419"
        querystring1 = {"address": ""+str(search.current_zip)+"", "store-type": "All", "min-latitude": "19.50139",
                       "max-latitude": ""+str(lat)+"", "min-longitude": "-68.01197", "max-longitude": ""+str(lng)+""}
        



        headers = {
            'Content-type': "*/*,multipart/form-data; boundary=--------------------------773008355060723902209115",
            'User-Agent': "PostmanRuntime/7.20.1",
            'Accept': "*/*",
            'Cache-Control': "no-cache",
            'Postman-Token': "4fa3632d-185c-4b7b-9811-f701eb949536,9ae7e127-2dcd-4ac3-9dff-c9f672d23431",
            'Host': "www.metrobyt-mobile.com",
            'Accept-Encoding': "gzip, deflate",
            'Content-Length': "0",
            'Connection': "keep-alive",
            'cache-control': "no-cache"
        }

        try:
            response1 = session.get(url, headers=headers, params=querystring1).json()
            current_results_len = len(response1)
        except:
            continue

        for loc in response1:
            locator_domain = 'https://www.metrobyt-mobile.com/'
            country_code = "US"
            store_number = loc["id"]
            location_type = loc["type"]
            location_name=''
            location_type=loc['type']
            if location_type:
                if "Corporate Store" in location_type:
                    continue
            else:
                location_type=''



            # try:
            #     location_name = loc["name"]
            # except:
            #     location_name = "<MISSING>"


            if location_type:
                location_name = "Metro by T-Mobile "+location_type.strip()
            else:
                location_name =  '<MISSING>'
            try:
                phone = loc["telephone"]
            except:
                phone = "<MISSING>"
            try:
                latitude = loc["location"]["latitude"]
                longitude = loc["location"]["longitude"]
            except:
                latitude = "<MISSING>"
                longitude = "<MISSING>"
            # logger.info(loc["address"]["streetAddress"])
            try:
                street_address = loc["location"]["address"]["streetAddress"]
            except:
                street_address = "<MISSING>"
            try:
                city = loc["location"]["address"]["addressLocality"]
            except:
                city = "<MISSING>"
            try:
                state = loc["location"]["address"]["addressRegion"]
            except:
                state = "<MISSING>"
            try:
                zipp = loc["location"]["address"]["postalCode"]
            except:
                zipp = "<MISSING>"
            if len(zipp.strip()) == 4:
                zipp = "0" + zipp
            #logger.info(zipp)
            # try:
            #     hours_of_operation = ""
            #     for key, value in loc["openingHours"].items():
            #         hours_of_operation += key + " " + value + " "
            # except:
            #     hours_of_operation = "<MISSING>"
            hours_of_operation=''
            for h in loc['openingHours']:
                hours_of_operation = ", ".join(h['days']) + ' ' + h['time']



            page_url = "<MISSING>"
            if phone== None:
                phone = "<MISSING>"

            if phone==".":
                phone = "<MISSING>"
            page_url = ("https://www.metrobyt-mobile.com/storelocator/"+state.lower()+'/'+city.lower().replace(" ",'-')+'/'+street_address.lower().replace(" ",'-'))
            store1 = []
            result_coords.append((latitude, longitude))
            store1.append(locator_domain if locator_domain else '<MISSING>')
            store1.append(location_name if location_name else '<MISSING>')
            store1.append(street_address if street_address else '<MISSING>')
            store1.append(city if city else '<MISSING>')
            store1.append(state if state else '<MISSING>')
            store1.append(zipp if zipp else '<MISSING>')
            store1.append(country_code if country_code else '<MISSING>')
            store1.append(store_number if store_number else '<MISSING>')
            store1.append(phone.strip() if phone.strip() else '<MISSING>')
            store1.append('<MISSING>')
            store1.append(latitude if latitude else '<MISSING>')
            store1.append(longitude if longitude else '<MISSING>')
            store1.append(hours_of_operation if hours_of_operation else '<MISSING>')
            store1.append(loc['name'].capitalize()  if loc['name'] else '<MISSING>')
            store1.append(page_url)
            if str(store1[2]+str(store1[-7])+store1[-1]) in addressess:
                continue
            addressess.append(str(store1[2]+str(store1[-7])+store1[-1]))
            # print("store1=======", store1)
            yield store1



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
