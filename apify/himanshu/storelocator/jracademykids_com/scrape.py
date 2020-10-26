from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import ast
import json
import csv



session = SgRequests()

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
    headers = {
        # 'User-Agent': "PostmanRuntime/7.19.0",
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
        'accept': 'application/json, text/javascript, */*; q=0.01',
    }

    addresses = []

    base_url = 'http://jracademykids.com'
    locator_domain = base_url
    location_name = "<MISSING>"
    street_address = "<MISSING>"
    city = "<MISSING>"
    state = "<MISSING>"
    zipp = "<MISSING>"
    country_code = "US"
    store_number = "<MISSING>"
    phone = "<MISSING>"
    location_type = "<MISSING>"
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    hours_of_operation = "<MISSING>"
    page_url = "<MISSING>"
    r = session.get("http://jracademykids.com/ja-locations/", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    script = json.loads(soup.find("script", text=re.compile(
        "var wpgmaps_localize_marker_data")).text.split("var wpgmaps_localize_marker_data = ")[1].split("};")[0] + "}")
    for key, value in script["1"].items():
        location_name = value["title"]
        address = value["address"]
        us_zip_list = re.findall(re.compile(
            r"\b[0-9]{5}(?:-[0-9]{4})?\b"), str(" ".join(address.split()[1:])))
        if us_zip_list:
            zipp = us_zip_list[-1]
        else:
            zipp = "80925"
        state_list = re.findall(
            r' ([A-Z]{2}) ', str(" ".join(address.split()[1:])))
        if state_list:
            state = state_list[-1]
        st = address.split(",")
        if " USA" in " ".join(st):
            st.remove(" USA")
        if len(st) == 3:
            street_address = st[0]
            city = st[1]
        elif len(st) == 2:
            st1 = st[0].split(".")
            # print(st1)
            if len(st1) > 1:
                street_address = " ".join(st1[:-1])
                # print(street_address)
                city = st1[-1]
            else:
                street_address = " ".join(" ".join(st1).split()[:-1])
                city = " ".join(st1).split()[-1]
        else:
            street_address = " ".join(st[0].split(state)[0].split()[:-2])
            city = " ".join(st[0].split(state)[0].split()[-2:])
        phone_tag = BeautifulSoup(value["desc"], "lxml")
        phone = re.findall(re.compile(
            ".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"), str(phone_tag))[0]
        page_url = base_url + value["linkd"]
        latitude = value["lat"].strip()
        longitude = value["lng"].strip()
        if "0" == latitude and "0" == longitude:
            r_loc = session.get(page_url, headers=headers)
            soup_loc = BeautifulSoup(r_loc.text, "lxml")
            latitude = soup_loc.find("iframe")["src"].split("!2d")[
                1].split("!2m")[0].split("!3d")[-1]
            longitude = soup_loc.find("iframe")["src"].split("!2d")[
                1].split("!2m")[0].split("!3d")[0]
        hours_of_operation = "<MISSING>"
        

        store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                 store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]
        # store = [x if x else "<MISSING>" for x in store]
        store = ['<MISSING>' if x == ' ' or x ==
                 None else x for x in store]
    

        if store[2] in addresses:
            continue
        addresses.append(store[2])

        # print("data = " + str(store))
        # print(
        #     '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
        yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
