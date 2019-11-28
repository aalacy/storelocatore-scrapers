import csv
import requests
from bs4 import BeautifulSoup
import re
import json
import sgzip

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    return_main_object = []
    addresses = []
    search = sgzip.ClosestNSearch()
    search.initialize()
    MAX_RESULTS = 50
    MAX_DISTANCE = 50
    current_results_len = 0     # need to update with no of count.
    zip_code = search.next_zip()

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }

    base_url = "https://www.happybank.com/"

    while zip_code:
        result_coords = []
        # print("zip_code === "+zip_code)
        location_url = "https://www.happybank.com/Locations?bh-sl-address="+str(zip_code)+"&locpage=search"
        try:

            r = requests.get(location_url,headers=headers)
        except:
            continue
        soup = BeautifulSoup(r.text, "lxml")
        locator_domain = base_url
        location_name = ""
        street_address = ""
        city = ""
        state = ""
        zipp = ""
        country_code = "US"
        store_number = ""
        phone = ""
        location_type = ""
        latitude = ""
        longitude = ""
        raw_address = ""
        hours_of_operation = ""
        script = soup.find_all("script",{"type":"text/javascript"})
        
        for i in script:
            if "dataRaw" in i.text:
                json_data = json.loads(i.text.split("JSON.stringify(")[1].split("),")[0])
                current_results_len = len(json_data)
                for data in json_data:
                    location_name = data["name"]
                    street_address = data['address'] + ' ' +data['address2'] 
                    city = data['city']
                    state = data['state']
                    zipp = data['postal']
                    country_code = data['category']
                    phone = data['phone']
                    # re.sub(r'[\W_]+', '', data['phone'])
                    location_type = data['category']
                    latitude = data['lat']
                    longitude = data['lng']
                    page_url = data['web']
                    phone = data['phone'].replace("BANK ","")
                    # phone1 = ''.join(filter(lambda x: x.isdigit(), data['phone']))
                    # index = 3
                    # char = '-'
                    # phone2 = phone1[:index] + char + phone1[index + 1:]
                    
                    # index = 7
                    # char = '-'
                    # phone = phone2[:index] + char + phone2[index + 1:]
                    # print(phone)
                    # print("-----------------------------",phone)
                    # print("https://www.happybank.com/Locations"+page_url)
                    r1 = requests.get("https://www.happybank.com/Locations"+page_url,headers=headers)
                    soup1 = BeautifulSoup(r1.text, "lxml")
                    hours_of_operation = " ".join(list(soup1.find("div",{"id":"hours"}).stripped_strings)).split("Special")[0]
                    result_coords.append((latitude, longitude))
                    store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                            store_number, phone, location_type, latitude, longitude, hours_of_operation,"https://www.happybank.com/Locations"+page_url]
                    if store[2] in addresses:
                        continue
                    addresses.append(store[2])
                    store = [x.encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]

                    # print("data = " + str(store))
                    # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
                    yield store

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
