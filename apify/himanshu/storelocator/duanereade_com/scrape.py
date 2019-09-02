import csv
import requests
from bs4 import BeautifulSoup
import re
import json


def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36',
        'Content-Type': 'application/json; charset=UTF-8'
    }

    # print("soup ===  first")

    base_url = "https://www.duanereade.com"
    # r = requests.get("https://www.rachellebery.ca/trouver-un-magasin/", headers=headers)
    # soup = BeautifulSoup(r.text, "lxml")
    return_main_object = []
    #   data = json.loads(soup.find("div",{"paging_container":re.compile('latlong.push')["paging_container"]}))
    # for link in soup.find_all('ul',re.compile('content')):
    #     print(link)

    # it will used in store data.
    locator_domain = base_url
    location_name = ""
    street_address = "<MISSING>"
    city = "<MISSING>"
    state = "<MISSING>"
    zipp = "<MISSING>"
    country_code = "US"
    store_number = "<MISSING>"
    phone = "<MISSING>"
    location_type = "duanereade"
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    raw_address = ""
    hours_of_operation = "<MISSING>"

    isFinish = False
    intdex = 1
    while isFinish is not True:
        r = requests.post("https://www.walgreens.com/locator/v1/stores/search", headers=headers,data='{"zip":"11576","r":"500000","requestType":"dotcom","s":"100","p":"'+str(intdex)+'"}')
        json_data = r.json()
        try:
            for address_list in json_data['results']:
                store_number = address_list["storeNumber"]
                latitude = address_list["latitude"]
                longitude = address_list["longitude"]
                zipp = address_list["store"]['address']['zip']
                city = address_list["store"]['address']['city']
                state = address_list["store"]['address']['state']
                location_name = city
                street_address = address_list["store"]['address']['street']

                hours_of_operation = "Pharmacy OpenTime : "+ address_list["store"]['pharmacyOpenTime']+"  "
                hours_of_operation += "Store CloseTime : "+ address_list["store"]['storeCloseTime']+" , "
                # hours_of_operation += address_list["store"]['nextAvailableDay']
                hours_of_operation += "Next Available Day : "+ str(address_list["store"]['nextAvailableDay']).replace('[',"").replace(']',"").replace('{',"").replace('}',"")
                phone = address_list["store"]['phone']['areaCode'] + address_list["store"]['phone']['number']

                # print("json_data ==== "+ str(phone))

                if phone is None or len(phone) == 0:
                    phone = "<MISSING>"
                
                store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                         store_number, phone, location_type, latitude, longitude, hours_of_operation]

                # print("data = " + str(store))
                # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')

                return_main_object.append(store)


            intdex += 1
            # isFinish = True
        except:
            isFinish = True


    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
