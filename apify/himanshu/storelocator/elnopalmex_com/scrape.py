import csv
import requests
from bs4 import BeautifulSoup
import re
import json


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
        'accept': '*/*',
    }

    addresses = []
    base_url = "http://www.elnopalmex.com"

    # print("Start ")

    r = requests.post("http://elnopalmex.com/locations.html", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")

    # print("second ")

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

    for script in soup.find("table", {"id": "Table_01"}).find_all("a"):
        page_url = base_url + "/" +str(script["href"])

        if "restaurants" in page_url:
            page_url = base_url + "/" + str(script["href"])
            # print("location ==== " + location_url)
            r = requests.get(page_url)
            soup = BeautifulSoup(r.text, 'lxml')
            iframe = soup.find('iframe')['src']
            try:
                geo_request = requests.get(iframe, headers=headers)
                geo_soup = BeautifulSoup(geo_request.text, "lxml")
            except Exception as e:
                continue
                #print("Error === " + str(e))
            for script_geo in geo_soup.find_all("script"):
                # print(script_geo)
                # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~`')
                try:
                    for script_geo in geo_soup.find_all("script"):
                        if "initEmbed" in script_geo.text:
                            geo_data = json.loads(script_geo.text.split(
                                "initEmbed(")[1].split(");")[0])[21][3][0][1]
                            lat = json.loads(script_geo.text.split(
                                "initEmbed(")[1].split(");")[0])[21][3][0][2][0]
                            lng = json.loads(script_geo.text.split(
                                "initEmbed(")[1].split(");")[0])[21][3][0][2][1]
                            phone = json.loads(script_geo.text.split(
                                "initEmbed(")[1].split(");")[0])[21][3][7]

                            # print("geo_data ===== " + geo_data)
                            us_zip_list = re.findall(re.compile(
                                r"\b[0-9]{5}(?:-[0-9]{4})?\b"), str(geo_data))
                            state_list = re.findall(
                                r' ([A-Z]{2}) ', str(geo_data))
                            # print(us_zip_list)
                            # print(state_list)
                            if len(geo_data.split(",")) > 3:
                                location_name = geo_data.split(',')[0]
                                street_address = geo_data.split(',')[1]
                                city = geo_data.split(',')[2]
                            else:
                                street_address = geo_data.split(',')[0]
                                city = geo_data.split(',')[1]
                                location_name = city

                            state = state_list[-1]
                            zipp = us_zip_list[-1]
                            latitude = str(lat)
                            longitude = str(lng)

                except Exception as e:
                    # print("Error === "+ str(e))
                    street_address = full_address_url.split("&q=")[1].split(",")[
                        0].replace("+", " ")
                    city = full_address_url.split("&q=")[1].split(",")[
                        1].replace("+", "")
                    state = full_address_url.split("&q=")[1].split(
                        ",")[2].split("&")[0].replace("+", "")
                    zipp = full_address_url.split(
                        "&t=")[0].split("+")[-1].replace("+", "")
                    latitude = full_address_url.split(
                        "&ll=")[1].split(",")[0]
                    longitude = full_address_url.split("&ll=")[1].split(",")[
                        1].split("&")[0]
                    location_name = city

            store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                     store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]

            if str(store[2]) + str(store[-3]) not in addresses:
                addresses.append(str(store[2]) + str(store[-3]))

                store = [x.encode('ascii', 'ignore').decode(
                    'ascii').strip() if x else "<MISSING>" for x in store]

                #print("data = " + str(store))
                #print(
                    # '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
                yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
