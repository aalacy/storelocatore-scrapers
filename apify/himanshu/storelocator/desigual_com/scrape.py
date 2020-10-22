import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import sgzip
session = SgRequests()
def write_output(data):
    with open('data.csv', mode='w',encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        for row in data:
            writer.writerow(row)
def fetch_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    address = []
    search = sgzip.ClosestNSearch()
    search.initialize()
    result_coords = []
    data_len = 0
    MAX_RESULTS = 100
    MAX_DISTANCE = 100
    coords = search.next_coord()
    while coords:
        try:
            r = session.get("https://www.desigual.com/on/demandware.store/Sites-dsglcom_prod_us-Site/en_US/Address-SearchStoreAddress?longitude="+str(coords[1])+"&latitude="+str(coords[0])+"&deliveryPoint=STORE&radius=7000&showOfficialStores=false&showOutlets=false&showAuthorized=false&showOnlyAllowDevosStores=false")
        except:
            continue
        data = r.json()
        mp = data['shippingAddresses']
        for i in data['shippingAddresses']:
            if i["countryCode"] not in ["US","CA"]:
                continue
            if 'address' in i:
                street_address = i['address'].replace("Orlando Florida Mall,","").replace("McArthurGlen Designer Outlet,","").replace("Miromar Outlets,","").replace("Shopping Center Dolphin Mall,","").replace("Miracle Mile Shops,","").strip()
            else:
                street_address = "<MISSING>"
            if 'name' in i:
                loacation_name = i['name']
            else:
                loacation_name = "<MISSING>"
            if "Desigual" not in loacation_name:
                continue
            if 'city' in i:
                city = i['city']
            else:
                city = "<MISSING>"
            if 'region' in i:
                state = i['regionSapId']
            else:
                state = "<MISSING>"
            if 'postalCode' in i:
                zipp =i['postalCode']
            else:
                zipp = "<MISSING>"
            if 'latitude' in i:
                latitude = i['latitude']
            else:
                latitude = "<MISSING>"
            if 'countryCode' in i:
                country_code = i['countryCode']
            else:
                country_code = "<MISSING>"
            if 'longitude' in i:
                longitude = i['longitude']
            else:
                longitude = "<MISSING>"
            result_coords.append((latitude, longitude))
            if 'storeId' in i:
                store_number = i['storeId'].replace("R","")
            else:
                store_number = "<MISSING>"
            if 'phone' in i:
                temp_phone = i['phone'].replace("+1","").replace(" ","").strip()
                phone = "("+temp_phone[:3]+")"+temp_phone[3:6]+"-"+temp_phone[6:]
            else:
                phone = "<MISSING>"
            hours = ""
            days = {1:"Sunday",2:"Monday",3:"Tuesday",4:"Wednesday",5:"Thursday",6:"Friday",7:"Saturday"}
            if "schedule" in mp and mp["schedule"]:
                store_hours = mp["schedule"]
                for hour in store_hours:
                    hours = hours + " " + days[hour["dayNumber"]] + " " + hour["value"]
                store.append(hours)
            if "Desigual" in loacation_name:
                store = []
                store.append("https://www.desigual.com/")
                store.append(loacation_name if loacation_name else "<MISSING>") 
                store.append(street_address if street_address else "<MISSING>")
                store.append(city if city else "<MISSING>")
                store.append(state if state else "<MISSING>")
                store.append(zipp if zipp else "<MISSING>")
                store.append(country_code if country_code else "<MISSING>")
                store.append(store_number if store_number else"<MISSING>") 
                store.append(phone if phone else "<MISSING>")
                store.append("<MISSING>")
                store.append(latitude if latitude else "<MISSING>")
                store.append(longitude if longitude else "<MISSING>")
                store.append(hours if hours else "<MISSING>")
                store.append("<MISSING>")
                if store[2] in address :
                    continue
                address.append(store[2])
                yield store
        
        if data_len < MAX_RESULTS:
            search.max_distance_update(MAX_DISTANCE)
        elif data_len == MAX_RESULTS:
            search.max_count_update(result_coords)
        else:
            raise Exception("expected at most " + str(MAX_RESULTS) + " results")
        coords = search.next_coord()
def scrape():
    data = fetch_data()
    write_output(data)

scrape()

