import csv
import requests
from bs4 import BeautifulSoup
import re
import json
import sgzip


def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
        "X-Requested-With": "XMLHttpRequest",
        "content-type": "application/x-www-form-urlencoded"
    }
    return_main_object = []
    addresses = []
    search = sgzip.ClosestNSearch()
    search.initialize()
    MAX_RESULTS = 30
    code = search.next_zip()
    while code:
        result_coords = []
        #print("remaining zipcodes: " + str(len(search.zipcodes)))
        zip_code = code
        #print('Pulling Zip %s...' % (zip_code))
        r_data = "address=" + zip_code + "&Submit=SEARCH"
        r = requests.post(
            "https://secure.gotwww.com/gotlocations.com/tommy/index.php", headers=headers, data=r_data)
        data_count = 0
        for store_text in r.text.split("L.marker([")[1:]:
            data_count = data_count + 1
            lat = store_text.split(",")[0]
            lng = store_text.split(",")[1].replace("]", "")
            result_coords.append((lat, lng))
            store_details = BeautifulSoup(store_text.split(
                ".bindPopup(")[1].split(");")[0], "lxml")
            address = store_details.find_all(
                "a")[-1]["href"].split("=")[-1].replace("+", " ")
            name = store_details.find("strong").text.strip()
            location_details = list(store_details.stripped_strings)
            phone = ""
            for part in location_details:
                if "PHONE:" in part:
                    phone = part.split("PHONE:")[1]
            hours = ""
            for i in range(len(location_details)):
                if "HOURS:" in location_details[i]:
                    for k in range(i + 1, len(location_details)):
                        if "PRODUCTS:" in location_details[k]:
                            break
                        hours = " " + hours + location_details[k]
                    break
            store = []
            store.append("https://www.tommy.com")
            store.append(name)
            store.append(" ".join(address.split(",")[:-4]).strip())
            if "  " in store[2]:
                store[2] = " ".join(
                    " ".join(address.split(",")[:-4]).split("  ")[0:]).strip()

            if ";" in store[2]:
                store[2] = " ".join(" ".join(address.split(
                    ",")[:-4]).split("  ")[-1].split(';')[0:]).strip()
            store[2] = store[2].replace("Outlets of Little Rock", "").replace("The Outlet Collection l", "").replace(
                "Outlet Marketplace", "").replace("Carolina Premium Outlets", "").replace("The Outlets of Maui", "").replace("BURNSIDE VILLAGE SHOPPING CENTRE", "").strip()
            if "28" == store[2]:
                store[2] = " ".join(address.split(",")[:-4]).strip()
            # print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
            if store[-1] in addresses:
                continue
            addresses.append(store[-1])
            store.append(address.split(",")[-4])
            store.append(address.split(",")[-3])
            store.append(address.split(
                ",")[-2] if address.split(",")[-2] != " " else "<MISSING>")
            store.append(address.split(",")[-1])
            if "US" not in store[-1] and "CA" not in store[-1]:
                continue
            store.append("<MISSING>")
            store.append(phone if phone else "<MISSING>")
            store.append("<MISSING>")
            store.append(lat)
            store.append(lng)
            store.append(hours if hours != "" else "<MISSING>")
            store.append("https://secure.gotwww.com/gotlocations.com/tommy/index.php")
            for i in range(len(store)):
                store[i] = store[i].replace('\\', '')
            # print(store)
            yield store
        # print("max count update")
        if data_count == MAX_RESULTS:
            search.max_count_update(result_coords)
        else:
            raise Exception("expected at most " +
                            str(MAX_RESULTS) + " results")
        code = search.next_zip()


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
