import csv
import requests
from bs4 import BeautifulSoup
import re
import json
import ast


def write_output(data):
    with open('data.csv', mode='w', encoding='utf8') as output_file:
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

    base_url = "https://urbanbrickspizza.com/"
    r = requests.get(base_url +'/locations' , headers=headers)
    soup = BeautifulSoup(r.text, "lxml")

    for part in soup.find_all("div", {"class": "main_color av_default_container_wrap container_wrap fullsize"}):
        for semi_part in part.find_all("div", {"class": "flex_column"}):
            temp_storeaddresss = list(semi_part.stripped_strings)

            lat = "<MISSING>"
            lag = "<MISSING>"
            if(len(temp_storeaddresss) > 2 ):

                if 'DIRECTIONS' in temp_storeaddresss:
                    temp_storeaddresss.remove('DIRECTIONS');
                    url = semi_part.find("a",{"class" : "avia-color-grey"})['href']
                    lat_find = url.split("@")
                    if(len(lat_find) == 2):
                        lat = lat_find[1].split(",")[0]
                        lag = lat_find[1].split(",")[1]
                    if 'THE RIM' in temp_storeaddresss:
                        lat_val = url.split("=")[1]
                        lat_val = lat_val.replace('(', ' ')
                        lat_val = lat_val.replace(')', ' ')
                        lat = lat_val.split(",")[0]
                        lag = lat_val.split(",")[1]
                if 'COMING SOON!' in temp_storeaddresss:
                    temp_storeaddresss.remove('COMING SOON!');
                if 'CATERING' in temp_storeaddresss:
                    temp_storeaddresss.remove('CATERING');
                if 'ONLINE ORDERS' in temp_storeaddresss:
                    temp_storeaddresss.remove('ONLINE ORDERS');
                location_name = temp_storeaddresss[0]
                row = temp_storeaddresss[1:]
                return_object = []
                return_object.append(base_url)
                return_object.append(location_name)
                return_object.append("<INACCESSIBLE>")
                return_object.append("<INACCESSIBLE>")
                return_object.append("<INACCESSIBLE>")
                return_object.append("<INACCESSIBLE>")
                return_object.append("US")
                return_object.append("<MISSING>")
                return_object.append("<MISSING>")
                return_object.append("Ueban brick")
                return_object.append(lat)
                return_object.append(lag)
                return_object.append("<MISSING>")
                return_object.append(row)
                return_main_object.append(return_object)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
