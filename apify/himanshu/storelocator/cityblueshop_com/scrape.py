import csv
import requests
from bs4 import BeautifulSoup
import re
import json
import ast


def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation",'raw_address'])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    return_main_object = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'
    }

    base_url = "https://www.cityblueshop.com/"
    r = requests.get(base_url + '/pages/locations', headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    for parts in soup.find_all("div", {"class": "rte-content colored-links"}):
        for semi_parts in parts.find_all("h3"):
            store_request = requests.get(semi_parts.find("a")['href'])
            store_soup = BeautifulSoup(store_request.text, "lxml")
            for inner_parts in store_soup.find_all("div", {"class": "rte-content colored-links"}):
                return_object = []
                temp_storeaddresss = list(inner_parts.stripped_strings)
                location_name = semi_parts.text
                age_index = [i for i, s in enumerate(temp_storeaddresss) if len(s) == 12 and s.replace("-","").isdigit()]
               # print("=>"+str(age_index))
                no = str(age_index)

                if (len(age_index) == 0):
                    raw_address = temp_storeaddresss[0]+" "+temp_storeaddresss[1];
                    phone = temp_storeaddresss[2].split(":")[1]
                    hour = temp_storeaddresss[3]+" "+temp_storeaddresss[4]+" "+temp_storeaddresss[5]
                else:
                    lst = temp_storeaddresss[:age_index[0]]
                    raw_address = " ".join(lst)
                    phone= temp_storeaddresss[age_index[0]]
                    hour_list =  temp_storeaddresss[age_index[0]: ]
                    hour = " ".join(hour_list)

                    return_object.append(base_url)
                    return_object.append(location_name)
                    return_object.append("<INACCESSIBLE>")
                    return_object.append("<INACCESSIBLE>")
                    return_object.append("<INACCESSIBLE>")
                    return_object.append("<INACCESSIBLE>")
                    return_object.append("US")
                    return_object.append("<MISSING>")
                    return_object.append(phone)
                    return_object.append("City Blue")
                    return_object.append("<MISSING>")
                    return_object.append("<MISSING>")
                    return_object.append(hour)
                    return_object.append(raw_address)
                    return_main_object.append(return_object)
                    print(return_object)
    print(return_main_object)
    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)

scrape()
