import csv
import sys
import requests
from bs4 import BeautifulSoup
import re
import json
# import pprint
# pp = pprint.PrettyPrinter(indent=4)
import sgzip


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
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
        "Authorization": "Bearer d168a942b4814ef725c58d116dd157544b1101864315194cf3cc1c51735ad459",
    }
    base_url = "https://www.aesop.com"

    addresses123 = []
    op = []
    addresses = []
    search = sgzip.ClosestNSearch()
    search.initialize()
    MAX_RESULTS = 100
    MAX_DISTANCE = 100
    # current_results_len = 0  # need to update with no of count.
    coord = search.next_coord()    # zip_code = search.next_zip()

    while coord:
        result_coords = []
        locator_domain = base_url
        location_name = ""
        street_address = ""
        city = ""
        state = ""
        zipp = ""
        zipcode = ''
        country_code = "US"
        store_number = ""
        phone = ""
        location_type = ""
        latitude = ""
        longitude = ""
        raw_address = ""
        hours_of_operation = ""
        lat = coord[0]
        lng = coord[1]
        # print("remaining zipcodes: " + str(len(search.zipcodes)))
        # print('Pulling Lat-Long %s,%s...' % (str(lat), str(lng)))
        # lat = -42.225
        # lng = -42.225
        # zip_code = 11576
        location_url = "https://cdn.contentful.com/spaces/q8kkhxjupn16/entries?locale=en&content_type=storeDetail&include=2&fields.location%5Bwithin%5D=" + \
            str(lat) + "%2C" + str(lng)
        # print('location_url ==' +location_url))
        try:
            r = requests.get(location_url, headers=headers)
        except:
            continue
        soup = BeautifulSoup(r.text, "lxml")
        k = json.loads(soup.text)['items']
        current_results_len = len(k)
        for i in k:
            city = ''
            if "country" in i['fields']:
                country_code = i['fields']["country"]
                if country_code.strip().lstrip() == "US" or country_code.strip().lstrip() == "CA":
                    # print("==============================")
                    v = i['fields']['formattedAddress']
                    name1 = i['fields']['storeName']
                    lat = i['fields']['location']['lat']
                    lng = i['fields']['location']['lon']
                    if "phone" in i['fields']:
                        phone = i['fields']['phone'].replace("=", "+")

                    ln = len(v.replace(", Canada", "").replace(
                        ", USA", "").split(","))
                    if ln == 4:
                        add_list = v.split(",")
                        if "" == add_list[-1]:
                            add_list.remove("")
                        state = add_list[-1].split()[0].strip()
                        zipp = add_list[-1].split()[-1].strip()
                        if "The Village at Corte Madera" not in add_list[0]:
                            street_address = " ".join(add_list[:-2]).strip()
                            city = add_list[-2].strip()
                        else:
                            street_address = " ".join(add_list[2].split()[:-2])
                            city = " ".join(add_list[2].split()[-2:])
                    elif ln == 3:
                        add_list = v.split(',')
                        if " USA" in add_list[-1]:
                            add_list.remove(" USA")
                        street_address = add_list[0].strip()
                        city = add_list[1].strip()
                        state = add_list[-1].split()[0].strip()
                        zipp = add_list[-1].split()[-1].strip()
                    elif ln == 2:
                        add_list = v.split(',')
                        if " Boston" in add_list[-1]:
                            street_address = " ".join(
                                add_list[0].split()[:-2]).strip()
                            city = add_list[-1].strip()
                            state = add_list[0].split()[-2].strip()
                            zipp = add_list[0].split()[-1].strip()
                        elif "NY10011" in add_list[-1]:
                            street_address = " ".join(
                                add_list[0].split()[:-2]).strip()
                            city = " ".join(add_list[0].split()[-2:])
                            state = add_list[-1].replace("10011", "").strip()
                            zipp = "10011"
                        elif len(add_list[-1].split()) > 2:
                            street_address = add_list[0].strip()
                            city = " ".join(add_list[-1].split()[:-2]).strip()
                            state = add_list[-1].split()[-2].strip()
                            zipp = add_list[-1].split()[-1].strip()
                        else:
                            street_address = " ".join(
                                add_list[0].split()[:-2]).strip()
                            city = " ".join(add_list[0].split()[-2:])
                            state = add_list[-1].split()[0].strip()
                            zipp = add_list[-1].split()[-1].strip()
                    else:
                        street_address = " ".join(v.split()[:-4]).strip()
                        city = " ".join(v.split()[-4:-2]).strip()
                        state = v.split()[-2].strip()
                        zipp = v.split()[-1].strip()
                    tem_var = []
                    tem_var.append("https://www.aesop.com")
                    tem_var.append(name1 if name1 else "<MISSING>")
                    tem_var.append(
                        street_address if street_address else "<MISSING>")
                    tem_var.append(city if city else "<MISSING>")
                    tem_var.append(state if state else "<MISSING>")
                    tem_var.append(zipp if zipp else "<MISSING>")
                    tem_var.append(country_code)
                    tem_var.append("<MISSING>")
                    tem_var.append(phone)
                    tem_var.append("<MISSING>")
                    tem_var.append(lat if lat else "<MISSING>")
                    tem_var.append(lng if lng else "<MISSING>")
                    tem_var.append("<MISSING>")
                    tem_var.append("<MISSING>")
                    tem_var = [x.encode('ascii', 'ignore').decode(
                        'ascii').strip() if type(x) == str else x for x in tem_var]
                    tem_var = ["<MISSING>" if x == "" else x for x in tem_var]
                    if tem_var[2] in addresses:
                        continue
                    addresses.append(tem_var[2])
                    yield tem_var
                    # print("data == " + str(tem_var))
                    # print("~~~~~~~~~~~")

        if current_results_len < MAX_RESULTS:
            # print("max distance update")
            search.max_distance_update(MAX_DISTANCE)
        elif current_results_len == MAX_RESULTS:
            # print("max count update")
            search.max_count_update(result_coords)
        else:
            raise Exception("expected at most " +
                            str(MAX_RESULTS) + " results")
        coord = search.next_coord()   # zip_code = search.next_zip()
        break


def scrape():
    data = fetch_data()

    write_output(data)


scrape()
