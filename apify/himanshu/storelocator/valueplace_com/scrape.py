import csv
from sgrequests import SgRequests
from datetime import datetime
import phonenumbers
from bs4 import BeautifulSoup
import re
import unicodedata
import sgzip


session = SgRequests()

def write_output(data):
    with open('data.csv',newline="", mode='w',encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    main_url = locator_domain = "https://www.valueplace.com"
    return_main_object = []
    addresses = []
    search = sgzip.ClosestNSearch()
    search.initialize(include_canadian_fsas=True)
    MAX_RESULTS = 200
    MAX_DISTANCE = 150
    coord = search.next_coord()
    while coord:
        
        result_coords = []
        # print("remaining zipcodes: " + str(search.zipcodes_remaining()))
        x = coord[0]
        y = coord[1]
        #print('Pulling Lat-Long %s,%s...' % (str(x), str(y)))
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36',
        }
        r = session.get("https://www-api.woodspring.com/v1/gateway/hotel/hotels?lat=" + str(x) + "&lng=" + str(y) + "&max=200&offset=0&radius=150",headers=headers)
        if "searchResults" not in r.json():
            search.max_distance_update(MAX_DISTANCE)
            coord = search.next_coord()
            continue
        data = r.json()["searchResults"]
        # print(data)
        for store_data in data:
            result_coords.append((store_data["geographicLocation"]["latitude"], store_data["geographicLocation"]["longitude"]))
            if store_data["address"]["countryCode"] != "US" and store_data["address"]["countryCode"] != "CA":
                continue
            location_name = store_data["hotelName"]
            # print("https://www-api.woodspring.com/v1/gateway/hotel/hotels/" + str(store_data["hotelId"]) + "?include=location,phones")
            location_request = session.get("https://www-api.woodspring.com/v1/gateway/hotel/hotels/" + str(store_data["hotelId"]) + "?include=location,phones,amenities,contacts,occupancy,policies,rooms",headers=headers)
            location_data = location_request.json()
            if "hotelStatus" in location_data["hotelInfo"]["hotelSummary"]:
                if location_data["hotelInfo"]["hotelSummary"]['hotelStatus'] == "Closed":
                    continue
            add = location_data["hotelInfo"]["hotelSummary"]["addresses"][0]
            street_address = ",".join(add["street"])
            if street_address in addresses:
                continue
            addresses.append(street_address)
            city = add["cityName"] 
            # if "," + store[-1] + "," in store[2]:
            #     store[2] = store[2].split("," + store[-1])[0]
            state = add["subdivisionCode"]
            zipp = add["postalCode"]
            country_code = add["countryCode"]
            store_number = "<MISSING>"
            try:
                phone = phonenumbers.format_number(phonenumbers.parse(str(location_data["hotelInfo"]["hotelSummary"]["phones"][0]["areaCode"] + location_data["hotelInfo"]["hotelSummary"]["phones"][0]["number"]), 'US'), phonenumbers.PhoneNumberFormat.NATIONAL)
                # phone= location_data["hotelInfo"]["hotelSummary"]["phones"][0]["areaCode"] + location_data["hotelInfo"]["hotelSummary"]["phones"][0]["number"]
            except:
                phone = phonenumbers.format_number(phonenumbers.parse(str(location_data["hotelInfo"]["hotelSummary"]["phones"][0]["number"] ), 'US'), phonenumbers.PhoneNumberFormat.NATIONAL)
                # phone = location_data["hotelInfo"]["hotelSummary"]["phones"][0]["number"]
            
            latitude = store_data["geographicLocation"]["latitude"]
            longitude = store_data["geographicLocation"]["longitude"]
            try:
                hours_of_operation = location_data['hotelInfo']['policyCodes'][0]['policyDescription'][0].replace("Hotel Office Hours :","").replace("|","").strip()
            except:
                # print("hours ==== ","https://www.woodspring.com" + str(store_data["hotelUri"]))
                # print("https://www-api.woodspring.com/v1/gateway/hotel/hotels/" + str(store_data["hotelId"]) + "?include=location,phones,amenities,contacts,occupancy,policies,rooms")
                if "hoursOfOperation" in location_data["hotelInfo"]["hotelSummary"]["hotelAmenities"][-1]:
                    hourslist = location_data["hotelInfo"]["hotelSummary"]["hotelAmenities"][-1]["hoursOfOperation"]
                    h_list =[]

                    for key,value in hourslist.items():
                        if "entireDay" in str(value[0]):
                            hours = "Daily 24 Hours"
                            h_list.append(hours)
                            
                        else:

                            hours = str(key)+": "+datetime.strptime(str(value[0]["startTime"]), "%H:%M").strftime("%I:%M %p")+" - "+datetime.strptime(str(value[0]["endTime"]), "%H:%M").strftime("%I:%M %p")
                            h_list.append(hours)
                        #     print(value[0][""])
                    
                    if "Daily 24 Hours" in " ".join(h_list):
                        hours_of_operation = "Daily 24 Hours"
                    else:
                        hours_of_operation = " ".join(h_list)
                    # print("hours ==== ","https://www.woodspring.com" + str(store_data["hotelUri"]))
                    # print(hours_of_operation)
                else:
                    hours_of_operation = "<MISSING>"
                
                    
                
            page_url = "https://www.woodspring.com" + str(store_data["hotelUri"])
            if "value-place" in page_url.split("/")[-1]:
                location_type = "valueplace"
            else:
                location_type = "woodspring"

            
            store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                                store_number, phone, location_type, latitude, longitude, hours_of_operation,page_url]
            for i in range(len(store)):
                if type(store[i]) == str:
                    store[i] = ''.join((c for c in unicodedata.normalize('NFD', store[i]) if unicodedata.category(c) != 'Mn'))
            store = [x.replace("–","-") if type(x) == str else x for x in store]
            store = [x.encode('ascii', 'ignore').decode('ascii').strip() if type(x) == str else x for x in store]
            yield store
            #print(store)

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
