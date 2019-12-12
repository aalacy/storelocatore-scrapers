import csv
import requests
from bs4 import BeautifulSoup
import re
import json
# from shapely.prepared import prep
# from shapely.geometry import Point
# from shapely.geometry import mapping, shape


def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation",
                         "page_url"])
        # Body
        for row in data:
            writer.writerow(row)
# def hasNumbers(inputString):
#     return any(char.isdigit() for char in inputString)

# countries = {}


# def getcountrygeo():
#     data = requests.get("https://raw.githubusercontent.com/datasets/geo-countries/master/data/countries.geojson").json()

#     for feature in data["features"]:
#         geom = feature["geometry"]
#         country = feature["properties"]["ADMIN"]
#         countries[country] = prep(shape(geom))


# def getplace(lat, lon):
#     point = Point(float(lon), float(lat))
#     for country, geom in countries.items():
#         if geom.contains(point):
#             return country

#     return "unknown"


def fetch_data():

    # getcountrygeo()  # it is use to get country from lat longitude

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
        'accept': '*/*',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8'
    }

    addresses = []
    base_url = "https://buckhorngrill.com/"

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
    page_url =""

    r = requests.get("https://buckhorngrill.com/location/")
    soup = BeautifulSoup(r.text,'lxml')
    for loc_row in soup.find_all('div',class_='location-row'):
        location_name = loc_row.find('h4').text
        address = loc_row.find('h4').find_next('p').text.split(',')
        if len(address) == 3:
            street_address = address[0].strip()
            city = address[1].strip()
            state = address[-1].strip()
            zipp = "<MISSING>"
        elif len(address) ==2:
            us_zip_list = re.findall(re.compile(r"\b[0-9]{5}(?:-[0-9]{4})?\b"), str(address[-1]))
            if us_zip_list:
                zipp = us_zip_list[-1]
                street_address = " ".join(address[0].split()[:-1]).strip().replace("San","").replace('Walnut',"").strip()
                city = " ".join(address[0].split()[-2:]).replace('Blvd','').replace('Rd','').replace('Suite#1339','').strip()
                state = address[-1].split()[0].strip()
            else:
                zipp = "<MISSING>"
                street_address = address[0]+ " "+" ".join(address[-1].split()[:2]).strip()
                city = address[-1].split()[-2].strip()
                state = address[-1].split()[-1].strip()
        else:

            if "CA" in address[0]:
                street_address = " ".join(address[0].split()[:-3]).strip()
                city = " ".join(address[0].split()[3:-1]).strip()
                state = "".join(address[0].split()[-1].strip())
                zipp = "<MISSING>"
            elif "California" in  address[0]:
                street_address =" ".join(address[0].split()[:-2]).strip()
                city = address[0].split()[-2]
                state = address[0].split()[-1]
                zipp = "<MISSING>"
            else:
                street_address = address[0].strip()
                city = "<MISSING>"
                state = "<MISSING>"
                zipp = "<MISSING>"
        # print(street_address+ " | "+city+ " | "+state+ " | "+zipp)
        phone_tag = loc_row.find('h4').find_next('p').find_next('p').text
        phone_list = re.findall(re.compile(".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"), str("".join(phone_tag)))
        if phone_list:
            phone = phone_list[0].strip()
        else:
            phone= "<MISSING>"
        loc_col = loc_row.find('div',class_='loc-col')
        list_hours = list(loc_col.stripped_strings)
        hours_of_operation = " ".join(list_hours[4:]).strip()
        page_url = loc_row.find(lambda tag: (tag.name == "a") and "View All Menus" in tag.text)['href']
        store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                 store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]

        if str(store[2]) + str(store[-3]) not in addresses:
            addresses.append(str(store[2]) + str(store[-3]))

            store = [x.encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]

            #print("data = " + str(store))
            #print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
            yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
