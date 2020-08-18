import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import usaddress as usd
import collections as coll

tm={
   'Recipient': 'recipient',
   'AddressNumber': 'address1',
   'AddressNumberPrefix': 'address1',
   'AddressNumberSuffix': 'address1',
   'StreetName': 'address1',
   'StreetNamePreDirectional': 'address1',
   'StreetNamePreModifier': 'address1',
   'StreetNamePreType': 'address1',
   'StreetNamePostDirectional': 'address1',
   'StreetNamePostModifier': 'address1',
   'StreetNamePostType': 'address1',
   'BuildingName': 'address1',
   'CornerOf': 'address1',
   'IntersectionSeparator': 'address1',
   'LandmarkName': 'address1',
   'USPSBoxGroupID': 'address1',
   'USPSBoxGroupType': 'address1',
   'OccupancyType': 'address1',
   'OccupancyIdentifier': 'address1',
   'PlaceName': 'city',
   'StateName': 'state',
   'ZipCode': 'zip_code',
}


session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w',newline="") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    addressess = []

    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36'
    
    }
    base_url = "https://www.kungfutea.com/"
    api = ['https://api.storepoint.co/v1/15dcedfc240d49/locations?rq','https://api.storepoint.co/v1/159b93ec517a46/locations?rq']
    for i in api:
        json_data = session.get(i, headers=headers).json()

        for idx,value in enumerate(json_data['results']['locations']):
            locator_domain = base_url
            soon = ["SOON)","soon)","Soon)"]
            if value['name'].split(" ")[-1] in soon:
                continue
            else:

                location_name = value['name'].strip()
                if location_name == "Pittsburgh - Kung Fu Tea Truck (Temporarily closed)":
                    continue
                # if location_name == (lambda location_name: location_name and " (coming soon)" in location_name):
                #     continue
                else:
                    street_address_raw = value['streetaddress'].replace(" (Garage A Food Court Entrance)","")
                    addr_format = usd.tag(street_address_raw,tm)
                    addr = list(addr_format[0].items())
                    # print(location_name)
                    # print(usd.parse(street_address_raw))
                    # print(addr)
                    # print(idx)
                    # print("================================")
            
                    street_address_ca = value['streetaddress'].replace(" (Garage A Food Court Entrance)","").split(" ")
                    if location_name == "Edmonton":
                        street_address = " ".join(street_address_ca[0:4])
                        city = street_address_ca[4]
                        state = street_address_ca[-3].replace(",","")
                        zipp = " ".join(street_address_ca[-2:])
                    elif location_name == "Welland":
                        street_address = " ".join(street_address_ca[0:3])
                        city = street_address_ca[3]
                        state = "ON"
                        zipp = " ".join(street_address_ca[-2:])
                    elif location_name == "East Village":
                        street_address = addr[0][1]
                        city = "New York"
                        state = "NY"
                        zipp = addr[3][1].replace(".","")
                    elif addr[0][1] == "234 Canal Street suite # 107":
                        street_address = addr[0][1]
                        city = addr[1][1]
                        state = "NY"
                        zipp ="<MISSING>"
                    elif addr[0][1] == "3440 Mchenry Ave Suite D14":
                        street_address = addr[0][1]
                        city = addr[1][1]
                        state ="CA"
                        zipp = addr[2][1]
                    else:
                        street_address = addr[0][1]
                        city = addr[1][1]
                        state = addr[2][1]
                        zipp = addr[3][1].replace(".","")

                    if location_name == "Edmonton":
                        country_code = "CA"
                    elif location_name == "Welland":
                        country_code = "CA"
                    else:
                        country_code = "US"

                    store_number = value['id']

                    if value['phone'] == "":
                        phone = "<MISSING>"
                    else:
                        phone = value['phone'].split("/")[0].strip()
                    location_type = "<MISSING>"
                    latitude = value['loc_lat']
                    longitude = value['loc_long']

                    if value['monday'] == "":
                        hours_of_operation = "<MISSING>"
                    else:
                        hours_of_operation = "monday: " + value['monday'] + ', ' + "tuesday: " + value['tuesday'] + ', ' + "wednesday: " + value['wednesday'] + ', ' + "thursday: " + value['thursday'] + ', ' + "friday: " + value['friday'] + ', ' + "saturday: " + value['saturday'] + ', ' + "sunday: " + value['sunday']

                    if location_name == "Edmonton":
                        page_url = "https://www.kungfutea.com/locations/can"
                    elif location_name == "Welland ":
                        page_url = "https://www.kungfutea.com/locations/can"
                    else:
                        page_url = "https://www.kungfutea.com/locations/usa"
                
                    store = []
                    store.append(locator_domain)
                    store.append(location_name)
                    store.append(street_address)
                    store.append(city)
                    store.append(state)
                    store.append(zipp)   
                    store.append(country_code)
                    store.append(store_number)
                    store.append(phone)
                    store.append(location_type)
                    store.append(latitude)
                    store.append(longitude)
                    store.append(hours_of_operation)
                    store.append(page_url)

                    if store[2] in addressess:
                        continue
                    addressess.append(store[2])
                    yield store



def scrape():
    data = fetch_data()
    write_output(data)

scrape()




