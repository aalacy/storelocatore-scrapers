import csv
import sys
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
from shapely.prepared import prep
from shapely.geometry import Point
from shapely.geometry import mapping, shape
import phonenumbers
session = SgRequests()

countries = {}

def getcountrygeo():
    data = session.get("https://raw.githubusercontent.com/datasets/geo-countries/master/data/countries.geojson").json()
    for feature in data["features"]:
        geom = feature["geometry"]
        country = feature["properties"]["ADMIN"]
        countries[country] = prep(shape(geom))

def getplace(lat, lon):
    if lon != "" and lat != "":
        point = Point(float(lon), float(lat))
    else:
        point = Point(0, 0)
    for country, geom in countries.items():
        if geom.contains(point):
            return country
    return "unknown"

def write_output(data):
    with open('data.csv', mode='w',newline="") as output_file:
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
    base_url = "https://www.circlek.com/qualityguaranteed"
    addresses = []
    locator_domain = base_url
    location_name = ""
    street_address = ""
    city = ""
    state = ""
    zipp = ""
    country_code = ""
    store_number = ""
    phone = ""
    location_type = ""
    latitude = ""
    longitude = ""
    hours_of_operation = ""
    location_url = "https://www.circlek.com/stores_new.php?lat=33.6&lng=-112.12&distance=10000000&services=gas&region=global"
    r = session.get(location_url, headers=headers).json()
    for key, value in r["stores"].items():
        latitude = value["latitude"].strip()
        longitude = value["longitude"].strip()
        country_name = getplace(latitude, longitude)
        if country_name in ["unknown", "United States of America","Canada"]:
            if "unknown" == country_name and str(value["country"]) not in ["US","CA","Canada"]:
                continue
            
            street_address = value["address"]
            store_number = value["cost_center"]
            city = value["city"]
            location_name = city
            location_type = ""

            for l_type in value["services"]:
                location_type += l_type['display_name'] + ","
            page_url = "https://www.circlek.com" + value["url"]

            r_loc = session.get(page_url, headers=headers)
            soup_loc = BeautifulSoup(r_loc.text, "lxml")
            try:
                csz = list(soup_loc.find(
                    "h2", class_="heading-small").stripped_strings)
                csz = [el.replace('\n', '') for el in csz]
                
                if len(csz) < 4:
                    state = "<MISSING>"
                else:
                    state = csz[-3].strip()
                zipp = csz[-1].strip()
        
                ca_zip_list = re.findall(
                    r'[A-Z]{1}[0-9]{1}[A-Z]{1}\s*[0-9]{1}[A-Z]{1}[0-9]{1}', str(zipp))
                us_zip_list = re.findall(re.compile(
                    r"\b[0-9]{5}(?:-[0-9]{4})?\b"), str(zipp))

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
                
                phone_tag = soup_loc.find(
                    "a", {"itemprop": "telephone"}).text.strip()
                phone_list = re.findall(re.compile(r".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"), str(phone_tag))
                if phone_list:
                    phone = phone_list[0]
                    phone = phonenumbers.format_number(phonenumbers.parse(phone, 'US'), phonenumbers.PhoneNumberFormat.NATIONAL)           
                else:
                    phone = "<MISSING>"
               
                hours_of_operation = " ".join(list(soup_loc.find(
                    "div", class_="columns large-12 middle hours-wrapper").stripped_strings)).replace("hours", "").strip()
            except:
                zipp = "<MISSING>"
                state = "<MISSING>"
                hours_of_operation = "<MISSING>"
                phone = "<MISSING>"
            if "." == street_address.strip():
                street_address = "<MISSING>"
            if "PEI" in state:
                state= "Prince Edward Island"
            store = [locator_domain, location_name.strip(), street_address.strip(), city.strip(), state.strip(), zipp.strip(), country_code,
                        store_number, phone.strip(), location_type, latitude, longitude, hours_of_operation.replace("hours", "").strip(), page_url]

            if str(store[2]) not in addresses:
                addresses.append(str(store[2]))
                store = [x if x else "<MISSING>" for x in store]
               
                yield store

def scrape():
    data = fetch_data()
    write_output(data)
scrape()
