import csv
from bs4 import BeautifulSoup
import sgzip
import re
import json
from sgrequests import SgRequests
session = SgRequests()



def write_output(data):
    with open('data.csv', mode='w', newline='') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    search = sgzip.ClosestNSearch()
    search.initialize(country_codes = ["UK"])
    MAX_RESULTS = 50
    MAX_DISTANCE = 10
    current_results_len = 0  # need to update with no of count.
    coord = search.next_coord()
    addresses = []
    while coord:
        result_coords = []

        lat = coord[0]
        lng = coord[1]
        # print(search.current_zip)
      # print("remaining zipcodes: " + str(len(search.zipcodes)))
        # print('Pulling Lat-Long %s,%s...' % (str(lat), str(lng)))

        base_url = "https://www.waitrose.com/"
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36,'
        }
        json_data = session.get("https://www.waitrose.com/shop/NearestBranchesCmd?latitude="+str(lat)+"&longitude="+str(lng)+"&fromMultipleBranch=true&_=1585897775137",headers=headers ).json()['branchList']
        current_results_len = len(json_data)
        for data in json_data:
            location_name = data['branchName']
            street_address = data['addressLine1']
            city = data['city']
            zipp = data['postCode']
            phone = data['phoneNumber']
            store_number = data['branchId']
            latitude = data['latitude']
            longitude = data['longitude']
            page_url = "https://www.waitrose.com/content/waitrose/en/bf_home/bf/"+str(store_number)+".html"
            # print(page_url)
            r1 = session.get(page_url,headers=headers)
            soup1 = BeautifulSoup(r1.text, "lxml")
            # addr = soup1.find("div",{"class":"col branch-details"}).text.replace(street_address,"").replace(city,"").replace(zipp,"").replace(phone,"").strip()
            try:
                hours_of_operation = " ".join(list(soup1.find("table").stripped_strings))
            except:
                hours_of_operation = "<MISSING>"

            result_coords.append((latitude,longitude))
            store = []
            store.append(base_url)
            store.append(location_name if location_name else "<MISSING>") 
            store.append(street_address if street_address else "<MISSING>")
            store.append(city if city else "<MISSING>")
            store.append("<INACCESSIBLE>")
            store.append(zipp if zipp else "<MISSING>")   
            store.append("UK")
            store.append(store_number if store_number else "<MISSING>") 
            store.append(phone)
            store.append("<MISSING>")
            store.append(latitude if latitude else "<MISSING>")
            store.append(longitude if longitude else "<MISSING>")
            store.append(hours_of_operation if hours_of_operation else "<MISSING>")
            store.append(page_url if page_url else "<MISSING>")
            if store[2] in addresses:
                    continue
            addresses.append(store[2])
            store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
            yield store

        if current_results_len < MAX_RESULTS:
            # print("max distance update")
            search.max_distance_update(MAX_DISTANCE)
        elif current_results_len == MAX_RESULTS:
            # print("max count update")
            search.max_count_update(result_coords)
        else:
            raise Exception("expected at most " + str(MAX_RESULTS) + " results")
        coord = search.next_coord()

def scrape():
    data = fetch_data()
    write_output(data)


scrape()
