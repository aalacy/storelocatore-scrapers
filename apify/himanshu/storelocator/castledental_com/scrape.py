import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import sgzip
import json
# import time



session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    # zips = sgzip.coords_for_radius(50)
    zips = sgzip.for_radius(50)
    return_main_object = []
    addresses = []

    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
        "Accept": "application/json, text/plain, */*",
        # "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    }

    # it will used in store data.
    base_url = "https://www.castledental.com/"
    locator_domain = "https://www.castledental.com/"
    location_name = ""
    street_address = "<MISSING>"
    city = "<MISSING>"
    state = "<MISSING>"
    zipp = "<MISSING>"
    country_code = "US"
    store_number = "<MISSING>"
    phone = "<MISSING>"
    location_type = "<MISSING>"
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    raw_address = ""
    hours_of_operation = "<MISSING>"
    page_url = "<MISSING>"

    for zip_code in zips:
        r = session.get(
            'https://api.smilebrands.com/public/facility/search/zip/' + str(zip_code), headers=headers)
        try:
            json_data = r.json()
        except:
            continue

        if json_data['data'] != None:

            for sid in json_data['data']:
                if sid['id'] != None:
                    store_id = sid['id']
                    r_loc = session.get(
                        'https://api.smilebrands.com/public/facility/id/' + str(store_id), headers=headers)
                    try:
                        r_loc_json = r_loc.json()
                    except:
                        continue
                    if r_loc_json['data']:
                        store_number = r_loc_json['data']['id']
                        location_name = r_loc_json['data']['name']
                        if r_loc_json['data']['address'] != None:
                            if r_loc_json['data']['careOf'] != None:
                                street_address = str(r_loc_json['data']['address']) + \
                                    " " + \
                                    str(r_loc_json['data']['careOf']).strip()
                            else:
                                street_address = r_loc_json['data']['address']
                        else:
                            street_address = "<MISSING>"
                        # print(street_address)

                        city = r_loc_json['data']['city']
                        state = r_loc_json['data']['state']
                        zipp = r_loc_json['data']['zip']
                        phone = r_loc_json['data']['phoneNumber']
                        latitude = r_loc_json['data']['latitude']
                        longitude = r_loc_json['data']['longitude']
                        if r_loc_json['data']['sundayHours'] is not None and r_loc_json['data']['mondayHours'] is not None and r_loc_json['data']['tuesdayHours'] is not None and r_loc_json['data']['wednesdayHours'] is not None and r_loc_json['data']['thursdayHours'] is not None and r_loc_json['data']['fridayHours'] is not None and r_loc_json['data']['saturdayHours'] is not None:  # 15040
                            hours_of_operation = "sunday: " + r_loc_json['data']['sundayHours'] + "    " + "monday: " + r_loc_json['data']['mondayHours'] + "    " + "tuesday: " + r_loc_json['data']['tuesdayHours'] + "     " + "wednesday: " + \
                                r_loc_json['data']['wednesdayHours'] + "   " + "thursday: " + r_loc_json['data']['thursdayHours'] + "    " + \
                                "friday: " + \
                                r_loc_json['data']['fridayHours'] + "    " + \
                                "saturday: " + \
                                r_loc_json['data']['saturdayHours']
                        else:
                            hours_of_operation = "<MISSING>"
                        page_url = r_loc_json['data']['publicUrl']
                        store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                                 store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]
                        store = [x if x else "<MISSING>" for x in store]

                        if store[1] + " " + store[2] in addresses:
                            continue
                        addresses.append(store[1] + " " + store[2])
                        # print("data = " + str(store))
                        # print(
                        #     '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')

                        return_main_object.append(store)
    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
