import csv
from  sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import sgzip
session = SgRequests()
import requests


def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():

    # for USA location 
    addresses = []
    search = sgzip.ClosestNSearch()    
    search.initialize(country_codes=["US"])
    MAX_RESULTS = 10000
    MAX_DISTANCE = 1000
    current_results_len = 0     # need to update with no of count.
    zip_code = search.next_zip()
    while zip_code:
        result_coords = []
        page = 1
        while True:
            base_url = "https://www.bossplow.com/"
            try:
                r = requests.get("https://www.bossplow.com/en/locator?countryCode=US&serviceType=Buy&postalCode="+str(zip_code)+"&resultType=Dealer&productType=354&categoryName=Contractor&productTypeName=&searchRadius="+str(MAX_DISTANCE)+"&page="+str(page))
            except:
                pass
            soup = BeautifulSoup(r.text, "lxml")
            if soup.find(lambda tag : (tag.name == "script") and "locations" in tag.text) == None:
                break
            json_data = json.loads(soup.find(lambda tag : (tag.name == "script") and "locations" in tag.text).text.split("locations:")[1].split("directionsButtonLabel")[0].replace("0}],","0}]").strip())
            current_results_len += len(json_data)
            for data in  json_data:
                location_name = data['Name']
                street_address = (data['Address']['AddressLine1'] + str(data['Address']['AddressLine2'])).replace("None","").strip()
                city = data['Address']['City']
                state = data['Address']['Region']
                zipp = data['Address']['PostalCode']
                country_code = data['Address']['Country']
                store_number = "<MISSING>"
                phone = data['Phone']
                location_type = data['DealerType']
                latitude = data['Latitude']
                longitude = data['Longitude']
                if data['Seasons'] != []:
                    hours = " ".join(data['Seasons'][0]['Hours'])
                else:
                    hours = "<MISSING>"
                
                page_url = "<MISSING>"
                
                if street_address in addresses:
                        continue
                addresses.append(street_address)

                result_coords.append((latitude,longitude))
                store = []
                store.append(base_url )
                store.append(location_name if location_name else '<MISSING>')
                store.append(street_address if street_address else '<MISSING>')
                store.append(city if city else '<MISSING>')
                store.append(state if state else '<MISSING>')
                store.append(zipp if zipp else '<MISSING>')
                store.append(country_code if country_code else '<MISSING>')
                store.append(store_number if store_number else '<MISSING>')
                store.append(phone if phone else '<MISSING>')
                store.append(location_type if location_type else '<MISSING>')
                store.append(latitude if latitude else '<MISSING>')
                store.append(longitude if longitude else '<MISSING>')
                store.append(hours if hours else '<MISSING>')
                store.append(page_url)
                # print("data ===="+str(store))
                # print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~`")
                yield store
                
            page += 1

        if current_results_len < MAX_RESULTS:
                # print("max distance update")
                search.max_distance_update(MAX_DISTANCE)
        elif current_results_len == MAX_RESULTS:
            # print("max count update")
            search.max_count_update(result_coords)
        else:
            raise Exception("expected at most " + str(MAX_RESULTS) + " results")
        zip_code = search.next_zip()
    





    ##### for Canada location


    addresses = []
    search = sgzip.ClosestNSearch()    
    search.initialize(country_codes=["CA"])
    MAX_RESULTS = 10000
    MAX_DISTANCE = 1000
    current_results_len = 0     # need to update with no of count.
    zip_code = search.next_zip()
    while zip_code:
        result_coords = []
        page = 1
        while True:
            base_url = "https://www.bossplow.com/"
            r = session.get("https://www.bossplow.com/en/locator?countryCode=CA&serviceType=Buy&postalCode="+str(zip_code)+"&resultType=Dealer&productType=354&categoryName=Contractor&productTypeName=&searchRadius="+str(MAX_DISTANCE)+"&page="+str(page))
            soup = BeautifulSoup(r.text, "lxml")
            if soup.find(lambda tag : (tag.name == "script") and "locations" in tag.text) == None:
                break
            json_data = json.loads(soup.find(lambda tag : (tag.name == "script") and "locations" in tag.text).text.split("locations:")[1].split("directionsButtonLabel")[0].replace("0}],","0}]").strip())
            current_results_len += len(json_data)
            for data in  json_data:
                location_name = data['Name']
                street_address = (data['Address']['AddressLine1'] + str(data['Address']['AddressLine2'])).replace("None","").strip()
                city = data['Address']['City']
                state = data['Address']['Region']
                zipp = data['Address']['PostalCode']
                country_code = data['Address']['Country']
                store_number = "<MISSING>"
                phone = data['Phone']
                location_type = data['DealerType']
                latitude = data['Latitude']
                longitude = data['Longitude']
                if data['Seasons'] != []:
                    hours = " ".join(data['Seasons'][0]['Hours'])
                else:
                    hours = "<MISSING>"
                
                page_url = "<MISSING>"
                
                if street_address in addresses:
                        continue
                addresses.append(street_address)

                result_coords.append((latitude,longitude))
                store = []
                store.append(base_url )
                store.append(location_name if location_name else '<MISSING>')
                store.append(street_address if street_address else '<MISSING>')
                store.append(city if city else '<MISSING>')
                store.append(state if state else '<MISSING>')
                store.append(zipp if zipp else '<MISSING>')
                store.append(country_code if country_code else '<MISSING>')
                store.append(store_number if store_number else '<MISSING>')
                store.append(phone if phone else '<MISSING>')
                store.append(location_type if location_type else '<MISSING>')
                store.append(latitude if latitude else '<MISSING>')
                store.append(longitude if longitude else '<MISSING>')
                store.append(hours if hours else '<MISSING>')
                store.append(page_url)
                # print("data ===="+str(store))
                # print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~`")
                yield store
                
            page += 1

        if current_results_len < MAX_RESULTS:
                # print("max distance update")
                search.max_distance_update(MAX_DISTANCE)
        elif current_results_len == MAX_RESULTS:
            # print("max count update")
            search.max_count_update(result_coords)
        else:
            raise Exception("expected at most " + str(MAX_RESULTS) + " results")
        zip_code = search.next_zip()
                   
def scrape():
    data = fetch_data()

    write_output(data)


scrape()
