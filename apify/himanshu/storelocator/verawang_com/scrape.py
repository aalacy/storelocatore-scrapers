import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
from shapely.prepared import prep
from shapely.geometry import Point
from shapely.geometry import mapping, shape



session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_ALL)
        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation",
                         "page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def hasNumbers(inputString):
    return any(char.isdigit() for char in inputString)


countries = {}


def getcountrygeo():
    data = session.get(
        "https://raw.githubusercontent.com/datasets/geo-countries/master/data/countries.geojson").json()

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


def fetch_data():
    getcountrygeo()  # it is use to get country from lat longitude

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
        'accept': '*/*',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8'
    }

    addresses = []
    base_url = "http://www.verawang.com"

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
    page_url = "https://www.verawang.com/wp-admin/admin-ajax.php/"

    r = session.post(page_url, headers=headers,
                      data="action=load_search_results&query=&type%5B%5D=13&type%5B%5D=14&type%5B%5D=15&type%5B%5D=16&type%5B%5D=57")
    json_data = r.json()
    # print("rtext === " + str(json_data))
    soup = BeautifulSoup(json_data["locations"], "lxml")
    # print(soup.prettify())

    for script in soup.find_all("div", {"data-js": "openInfoBox"}):

        latitude = str(script["data-lat"])
        longitude = str(script["data-lng"])
        store_number = script["data-id"]
        location_name = script.find("h4").text
        # print(script.prettify())
        # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')

        country_name = getplace(latitude, longitude)
        # print("geo_url === " + str(country_name))
        if "United States of America" != country_name and "Canada" != country_name:
            continue
        if "Canada" == country_name:
            country_code = "CA"
        else:
            country_code = "US"
        address_list = list(script.find("address").stripped_strings)

        phone_list = re.findall(re.compile(
            ".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"), str(" ".join(address_list)))
        if phone_list:
            phone = phone_list[-1]
        else:
            phone = "<MISSING>"
        if len(address_list) == 6:
            street_address = " ".join(address_list[:2]).strip()
            city = address_list[2].split(',')[0].strip()
            state = address_list[2].split(',')[-1].strip()
            # zipp = address_list[3].strip()
        elif len(address_list) == 5:
            phone_list = re.findall(re.compile(
                ".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"), str("".join(address_list[-1])))
            if phone_list:
                street_address = " ".join(address_list[:2]).strip()
                city = address_list[2].split(',')[0].strip()
                state = address_list[2].split(',')[-1].strip()
                # zipp = address_list[3].strip()
            else:
                phone_list = re.findall(re.compile(
                    ".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"), str("".join(address_list[-2])))
                if phone_list:
                    street_address = address_list[0].strip()
                    city = address_list[1].split(',')[0].strip()
                    state = address_list[1].split(',')[-1].strip()
                    # zipp = address_list[2].strip()
                else:
                    street_address = address_list[1].strip()
                    city = address_list[2].split(',')[0].strip()
                    state = address_list[2].split(',')[-1].strip()
                    # zipp = address_list[-2].strip()
        elif len(address_list) == 4:
            phone_list = re.findall(re.compile(
                ".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"), str("".join(address_list[-2])))
            us_zip_list = re.findall(re.compile(
                r"\b[0-9]{5}(?:-[0-9]{4})?\b"), str(address_list[-1]))
            if "Canada" in " ".join(address_list) or phone_list:
                street_address = address_list[0].strip()
                city = address_list[1].split(',')[0].strip()
                state = address_list[1].split(',')[1].split()[0].strip()
                # zipp = " ".join(address_list[1].split(',')[
                # 1].split()[1:]).strip()
                # print(street_address+ "  | "+city +" | "+state+" | "+zipp)
            elif us_zip_list:
                street_address = " ".join(address_list[:2]).strip()
                city = address_list[2].split(',')[0].strip()
                state = address_list[2].split(',')[-1].strip()
                # zipp = address_list[-1].strip()
            else:
                street_address = address_list[0].strip()
                city = address_list[1].split(',')[0].strip()
                state = address_list[1].split(',')[1].strip()
                # zipp = address_list[-2].strip()
        elif len(address_list) == 3:
            street_address = address_list[0].strip()
            # ca_zip_list = re.findall(
            #     r'[A-Z]{1}[0-9]{1}[A-Z]{1}\s*[0-9]{1}[A-Z]{1}[0-9]{1}', str(address_list[1]))
            # us_zip_list = re.findall(re.compile(
            #     r"\b[0-9]{5}(?:-[0-9]{4})?\b"), str(address_list[1]))
            # if us_zip_list:
            #     zipp = us_zip_list[-1]
            # elif ca_zip_list:
            #     zipp = ca_zip_list[-1]
            # else:
            #     zipp = "<MISSING>"
            if len(address_list[1].split(',')) > 1:
                city = address_list[1].split(',')[0].strip()
                state_tag = address_list[1].split(',')[1].strip()
                if hasNumbers(state_tag) == True:
                    # stata_tag = state
                    state = " ".join(state_tag.split()[:-1]).replace("V6B", "")

                else:
                    state = state_tag

            else:
                city = address_list[1].split()[0].strip()
                state = address_list[1].split()[1].strip()
        else:
            pass
        # if "1888 Coney Island Avenue" in street_address:
            # print(address_list)

        us_zip_list = re.findall(re.compile(
            r"\b[0-9]{5}(?:-[0-9]{4})?\b"), str(" ".join(address_list)))
        ca_zip_list = re.findall(
            r'[A-Z]{1}[0-9]{1}[A-Z]{1}\s*[0-9]{1}[A-Z]{1}[0-9]{1}', str(" ".join(address_list)))
        # print(address_list)
        # print(us_zip_list, ca_zip_list)
        if us_zip_list:
            zipp = us_zip_list[-1].strip()
        elif ca_zip_list:
            zipp = ca_zip_list[-1].strip()
        else:
            # zipp = ''
            req = session.post(
                "https://www.verawang.com/wp-admin/admin-ajax.php?action=asl_load_stores&nonce=42170ab7d4&load_all=1&layout=1", headers=headers).json()
            z = []
            for loc in req:
                if loc["country"] in ["Canada", "United States"]:
                    st = loc["street"]
                    if st in street_address:
                        # print(st)
                        if loc["postal_code"] != None:
                            zip = loc["postal_code"].strip()

                        else:
                            # print(st)
                            zip = "<MISSING>"

                        z.append(zip)
                    else:
                        zip = "<MISSING>"
            # print(z)
            if z != []:
                zipp = "".join(z)
            else:
                zipp = "<MISSING>"
            # print(street_address, zipp)

        store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                 store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]

        if str(store[2]) + str(store[-3]) not in addresses:
            addresses.append(str(store[2]) + str(store[-3]))

            store = [x.encode('ascii', 'ignore').decode(
                'ascii').strip() if x else "<MISSING>" for x in store]

            # print("data = " + str(store))
            # print(
            #     '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
            yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
