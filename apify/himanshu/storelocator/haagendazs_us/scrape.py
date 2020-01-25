
import urllib.parse
import requests
from bs4 import BeautifulSoup
import re
# import ast
import json
# import sgzip
import csv


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
    headers = {
        'User-Agent': "PostmanRuntime/7.19.0",
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
        'accept': 'application/json, text/javascript, */*; q=0.01',
    }
    # coords = sgzip.coords_for_radius(50)
    # search = sgzip.ClosestNSearch()
    # search.initialize()
    # addresses = []
    # MAX_RESULTS = 100
    # MAX_DISTANCE = 30
    # current_results_len = 0
    # coords = search.next_coord()

    # while coords:
        # print("remaining zipcodes: " + str(len(search.zipcodes)))
    result_coords = []
    base_url = 'https://www.haagendazs.us'
    locator_domain = "https://www.haagendazs.us"
    location_name = "<MISSING>"
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
    hours_of_operation = "<MISSING>"
    page_url = "<MISSING>"

    # try:
    #     r
    #     r = requests.post("https://www.haagendazs.us/locator/ws/"+str(search.current_zip)+"/" + str(
    #         coords[0]) + "/" + str(coords[1]) + "/5/0/2452?lat=" + str(coords[0]) + "&lon=" + str(coords[1]) + "&radius=25&zipcode=&BrandFlavorID=2452&targetsearch=30", headers=headers).json()

    # except:
    #     pass
    json_data = requests.get("https://www.haagendazs.us/locator/ws/11211/40.7093358/-73.9565551/25/0/2452?lat=40.7093358&lon=-73.9565551&radius=5&zipcode=11211&BrandFlavorID=2452&targetsearch=3").json()
    # print(r)
    for data in json_data:


        # print(data)
        if data['URL']:
            page_url ="https://www.haagendazs.us"+ data['URL']
            html = requests.get(page_url)
            soup = BeautifulSoup(html.text,"html.parser")
            # print(soup)
            # exit()

            try:
                hours_of_operation = " ".join(list(soup.find("div",attrs={"class":"office-hours"}).stripped_strings))
            except:
                hours_of_operation = ""
        # print(all_rec)
        # exit()

        store = [locator_domain, data['Name'], data['Shop_Street__c'], data['Shop_City__c'], data['Shop_State_Province__c'], data['Shop_Zip_Postal_Code__c'], country_code,
         store_number, data['phone'], location_type, data['lat__c'], data['lon__c'], hours_of_operation, page_url]
        store = [x if x else "<MISSING>" for x in store]
        # store = [el.replace('\n', ' ') for el in store]
        store = [str(x).encode('ascii', 'ignore').decode(
            'ascii').strip() if x else "<MISSING>" for x in store]
        yield store
        # print(store)
    # print("https://www.haagendazs.us/locator/ws/"+str(search.current_zip)+"/" + str(
    #         coords[0]) + "/" + str(coords[1]) + "/5/0/2452?lat=" + str(coords[0]) + "&lon=" + str(coords[1]) + "&radius=25&zipcode=&BrandFlavorID=2452&targetsearch=30")
    # print(r)
    # if r != []:
        # current_results_len = len(r)
        #print(current_results_len)
    # for loc in r:
    #     # store_number = loc["Id"]
    #     location_name = loc["Name"]
    #     latitude = loc["lat__c"]
    #     longitude = loc["lon__c"]
    #     street_address = loc["Shop_Street__c"]
    #     city = loc["Shop_City__c"]
    #     state = loc["Shop_State_Province__c"]
    #     zipp = loc["Shop_Zip_Postal_Code__c"]
    #     country_code = "US"
    #     phone = loc["phone"]
    #     page_url = loc["URL"]
    #     if page_url:
    #         page_url = "https://www.haagendazs.us" + loc["URL"]
    #         r_loc = requests.get(page_url, headers=headers)
    #         soup_loc = BeautifulSoup(r_loc.text, "lxml")
    #         try:
    #             hours_of_operation = " ".join(
    #                 list(soup_loc.find("div", class_="box information-hours").stripped_strings))
    #         except:
    #             hours_of_operation = "<MISSING>"
    #         # print(hours_of_operation)
    #     else:
    #         page_url = "<MISSING>"
    #     # print(location_name)
    #     print(page_url)
    #     result_coords.append((latitude, longitude))

    #     store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
    #              store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]
    #     store = [x if x else "<MISSING>" for x in store]
    #     store = [el.replace('\n', ' ') for el in store]
    #     store = [str(x).encode('ascii', 'ignore').decode(
    #         'ascii').strip() if x else "<MISSING>" for x in store]

    #     if store[2] in addresses:
    #         #print(store[2])
    #         continue
    #     addresses.append(store[2])

    #     # print("data = " + str(store))
    #     # print(
    #     #     '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
    #     yield store

        # if current_results_len < MAX_RESULTS:
        #     # print("max distance update")
        #     search.max_distance_update(MAX_DISTANCE)
        # elif current_results_len == MAX_RESULTS:
        #     # print("max count update")
        #     search.max_count_update(result_coords)
        # # else:
        # #     raise Exception("expected at most " +
        # #                     str(MAX_RESULTS) + " results")
        # coords = search.next_coord()


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
