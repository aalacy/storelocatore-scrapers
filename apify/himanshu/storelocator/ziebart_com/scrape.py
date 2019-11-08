import csv
import requests
from bs4 import BeautifulSoup
import re
import json
import sgzip
import urllib.parse


def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation",
                         "page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    return_main_object = []
    addresses = []
    search = sgzip.ClosestNSearch()
    search.initialize()
    MAX_RESULTS = 20
    MAX_DISTANCE = 100
    current_results_len = 0  # need to update with no of count.
    zip_code = search.next_zip()

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }

    base_url = "https://www.ziebart.com"

    url_for_param = "https://www.ziebart.com/find-my-local-ziebart"
    r_param = requests.get(url_for_param, headers=headers)
    soup_param = BeautifulSoup(r_param.text, "lxml")
    # print("print  === "+ str(soup_param))
    __VIEWSTATE = urllib.parse.quote(soup_param.find("input", {"id": "__VIEWSTATE"})["value"])
    __EVENTVALIDATION = urllib.parse.quote(soup_param.find("input", {"id": "__EVENTVALIDATION"})["value"])

    # print("__VIEWSTATE === " + __VIEWSTATE)
    # print("__EVENTVALIDATION === " + __EVENTVALIDATION)

    while zip_code:
        result_coords = []

        # print("remaining zipcodes: " + str(len(search.zipcodes)))
        # print("zip_code === " + zip_code)

        location_url = "https://www.ziebart.com/find-my-local-ziebart"
        # zip_code = "07420"

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
            "X-Requested-With": "XMLHttpRequest",
            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
        }

        body = '__VIEWSTATE=' + __VIEWSTATE + '&__EVENTVALIDATION=' + __EVENTVALIDATION + '&ctl00%24cph_main%24C011%24rtbLocation=' + str(
            zip_code) + '&ctl00_cph_main_C011_rtbLocation_ClientState=%7B%22enabled%22%3Atrue%2C%22emptyMessage%22%3A%22%22%2C%22validationText%22%3A%22' + str(
            zip_code) + '%22%2C%22valueAsString%22%3A%22' + str(
            zip_code) + '%22%2C%22lastSetTextBoxValue%22%3A%22' + str(
            zip_code) + '%22%7D&ctl00%24cph_main%24C011%24ddlMiles=100&ctl00%24cph_main%24C011%24btnFindZiebart=Find+My+Local+Ziebart'
    
        while True:
            try:
                r_locations = requests.post(location_url, headers=headers, data=body)
                break
            except:
                continue
        soup_locations = BeautifulSoup(r_locations.text, "lxml")

        tag_store = soup_locations.find_all(lambda tag: (tag.name == "a") and "Store Details" == tag.text.strip())

        current_results_len = len(tag_store)  # it always need to set total len of record.
        # print("current_results_len === " + str(current_results_len))

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
        page_url = ""

        for tag in tag_store:
            if tag.parent.parent.find_previous_sibling('tr') == None:
                continue
            addresses_list = list(tag.parent.parent.find_previous_sibling('tr').stripped_strings)
            print(addresses_list)
            page_url = base_url + tag["href"]
            # print("address_list === " + str(addresses_list))
            # print("page_url === " + str(page_url))

            location_name = addresses_list[0].strip()
            # store_number = addresses_list[0].strip().split("#")[1]
            street_address = addresses_list[2].strip()

            zipp = ""
            state = ""
            ca_zip_list = re.findall(r'[A-Z]{1}[0-9]{1}[A-Z]{1}\s*[0-9]{1}[A-Z]{1}[0-9]{1}',
                                    str(" ".join(addresses_list)))
            us_zip_list = re.findall(re.compile(r"\b[0-9]{5}(?:-[0-9]{4})?\b"), str(" ".join(addresses_list)))
            state_list = re.findall(r' ([A-Z]{2}) ', " ".join(addresses_list))

            phone_list = re.findall(re.compile(".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"), str(" ".join(addresses_list)))

            if phone_list:
                phone = phone_list[0]
            else:
                phone = ""

            if state_list:
                state = state_list[0]

            if ca_zip_list:
                zipp = ca_zip_list[-1]
                country_code = "CA"

            if us_zip_list:
                zipp = us_zip_list[-1]
                country_code = "US"

            city = addresses_list[3].strip().replace(zipp, "").replace(state, "").replace(",", "")

            while True:
                try:
                    r_hours = requests.post(page_url, headers=headers, data=body)
                    break
                except:
                    continue
            soup_hours = BeautifulSoup(r_hours.text, "lxml")

            hours_list = list(soup_hours.find("table", {"id": "specification_responsive"}).stripped_strings)
            hours_of_operation = ""
            for i in range(int(len(hours_list) / 2)):
                hours_of_operation += hours_list[i] + " " + hours_list[i + int(len(hours_list) / 2)] + " "

            geo_url = soup_hours.find("iframe",{"src":re.compile("https://www.google.com/maps")})["src"]
            # print("geo_url === " + str(geo_url))
            latitude = geo_url.split("&sspn=")[1].split(",")[0]
            longitude = geo_url.split("&sspn=")[1].split(",")[1].split("&")[0]

            result_coords.append((latitude, longitude))
            store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                    store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]

            if str(store[1]) + str(store[2]) not in addresses:
                addresses.append(str(store[1]) + str(store[2]))

                store = [x.encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]

                print("data = " + str(store))
                print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
                yield store

        if current_results_len < MAX_RESULTS:
            # print("max distance update")
            search.max_distance_update(MAX_DISTANCE)
        elif current_results_len == MAX_RESULTS:
            # print("max count update")
            search.max_count_update(result_coords)
        else:
            raise Exception("expected at most " + str(MAX_RESULTS) + " results")
        zip_code = search.next_zip()
        # break

def scrape():
    data = fetch_data()
    write_output(data)


scrape()
