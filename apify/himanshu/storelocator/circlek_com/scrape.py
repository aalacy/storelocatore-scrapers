import csv
import sys
import requests
from bs4 import BeautifulSoup
import re
import json
from shapely.prepared import prep
from shapely.geometry import Point
from shapely.geometry import mapping, shape

countries = {}
   

def getcountrygeo():
    data = requests.get("https://raw.githubusercontent.com/datasets/geo-countries/master/data/countries.geojson").json()

    for feature in data["features"]:
        geom = feature["geometry"]
        country = feature["properties"]["ADMIN"]
        countries[country] = prep(shape(geom))


def getplace(lat, lon):
    point = Point(float(lon), float(lat))
    for country, geom in countries.items():
        if geom.contains(point):
            return country

    return "unknown"



def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    getcountrygeo()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }
    base_url = "https://www.circlek.com"

    addresses = []
    result_coords = []
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

    location_url = "https://www.circlek.com/stores_new.php?lat=40.8&lng=-73.65&distance=100000&services=&region=global"
    r = requests.get(location_url, headers=headers).json()
    for key, value in r["stores"].items():
        latitude = value["latitude"]
        longitude = value["longitude"]
        country_name = getplace(latitude, longitude)

        if "United States of America" != country_name and "Canada" != country_name:
            continue
        # print("~~~~~~~~country_name~~~~~~~~~~~~~~~~~~~~~",country_name)
        
        street_address = value["address"]
        store_number = value["cost_center"]
        # street_address = value["address"]
        city = value["city"]
        location_name = city
        location_type = value["display_brand"]
        page_url = "https://www.circlek.com" + value["url"]
        # print(page_url)
        r_loc = requests.get(page_url, headers=headers)
        soup_loc = BeautifulSoup(r_loc.text, "lxml")
        try:
            csz = list(soup_loc.find(
                "h2", class_="heading-small").stripped_strings)
            csz = [el.replace('\n', '') for el in csz]
            # print(csz)
            if len(csz) < 4:
                state = "<MISSING>"
            else:
                state = csz[-3].strip()
            zipp = csz[-1].strip()
            # print(zipp)
            # print("~~~~~~~~~~~~~~~~~~~~~~~~")
            # if len(zipp) == 6 or len(zipp) ==7:



            ca_zip_list = re.findall(
                r'[A-Z]{1}[0-9]{1}[A-Z]{1}\s*[0-9]{1}[A-Z]{1}[0-9]{1}', str(zipp))
            us_zip_list = re.findall(re.compile(
                r"\b[0-9]{5}(?:-[0-9]{4})?\b"), str(zipp))

            # print("~us_zip_list~~~~~~~~~~~~~~~~~~~~~~",us_zip_list,"~~~~~~~~~~~~~~~ca_zip_list~~~~~~~",ca_zip_list)
            if ca_zip_list:
                zipp = ca_zip_list[-1]
                country_code = "CA"
            

            elif us_zip_list:
                zipp = us_zip_list[-1]
                country_code = "US"
            else:
                zipp = "<MISSING>"
                if "Canada" in country_name:
                    country_code = "CA"
                else:
                    country_code = "US"
            # print(zipp,country_code)
        
            phone = soup_loc.find(
                "a", {"itemprop": "telephone"}).text.strip()
            hours_of_operation = " ".join(list(soup_loc.find(
                "div", class_="columns large-12 middle hours-wrapper").stripped_strings)).replace("hours", "").strip()
        except:
            zipp = "<MISSING>"
            state = "<MISSING>"
            hours_of_operation = "<MISSING>"
            phone = "<MISSING>"
        # print(phone)
        if "."==street_address.strip():
            street_address = "<MISSING>"

        store = [locator_domain, location_name.encode('ascii', 'ignore').decode('ascii').strip(), street_address.encode('ascii', 'ignore').decode('ascii').strip(), city.encode('ascii', 'ignore').decode('ascii').strip(), state.encode('ascii', 'ignore').decode('ascii').strip(), zipp.encode('ascii', 'ignore').decode('ascii').strip(), country_code,
                    store_number, phone.encode('ascii', 'ignore').decode('ascii').strip(), location_type, latitude, longitude, hours_of_operation.replace("hours", "").encode('ascii', 'ignore').decode('ascii').strip(), page_url]

        if str(store[2]) + str(store[-3]) not in addresses:
            addresses.append(str(store[2]) + str(store[-3]))
            store = [x if x else "<MISSING>" for x in store]
           # print("data = " + str(store))
            #print(
                #'~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
            yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
