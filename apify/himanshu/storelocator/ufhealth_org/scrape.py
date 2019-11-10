import csv
import time
import requests
from bs4 import BeautifulSoup
import re
import json



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


def request_wrapper(url, method, headers, data=None):
    request_counter = 0
    if method == "get":
        while True:
            try:
                r = requests.get(url, headers=headers)
                return r
                break
            except:
                time.sleep(2)
                request_counter = request_counter + 1
                if request_counter > 10:
                    return None
                    break
    elif method == "post":
        while True:
            try:
                if data:
                    r = requests.post(url, headers=headers, data=data)
                else:
                    r = requests.post(url, headers=headers)
                return r
                break
            except:
                time.sleep(2)
                request_counter = request_counter + 1
                if request_counter > 10:
                    return None
                    break
    else:
        return None


def fetch_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }

    base_url = "https://www.ufhealth.org"
    addresses = []

    r_search_location = request_wrapper("https://ufhealth.org/search/locations", "get", headers=headers)
    soup_search_location = BeautifulSoup(r_search_location.text, "lxml")
    # print("soup_search_location === "+ str(soup_search_location))
    for cat_tag in soup_search_location.find_all("option", {"value": re.compile("im_field_dpt_specialty:")}):

        cat_url = "https://ufhealth.org/search/locations?f%5B0%5D=im_field_dpt_specialty%3A" + \
                  cat_tag["value"].split("im_field_dpt_specialty:")[1].split('"')[0]

        while True:
            # print(cat_tag.text + " == type_tag  === " + str(cat_url))
            r_locations = request_wrapper(cat_url, "get", headers=headers)

            if r_locations is None:
                continue

            soup_locations = BeautifulSoup(r_locations.text, "lxml")
            # print("soup_locations = "+ str(soup_locations.find("a",{"title":"Go to next page"})))

            for single_location in soup_locations.find_all("li", {"class": "search-result divclick"}):

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
                raw_address = ""
                hours_of_operation = ""
                page_url = single_location.find("a")["href"]

                # page_url = "https://ufhealth.org/uf-health-congenital-heart-center/maps"

                # print("page_url ==== " + page_url)
                # do your logic here.
                r_store = request_wrapper(page_url + "/maps", "get", headers=headers)

                if r_store is None:
                    continue
                soup_store = BeautifulSoup(r_store.text, "lxml")

                location_type = cat_tag.text.split("(")[0]

                if soup_store.find("div", {"class": "street-address"}):
                    street_address = " ".join(list(soup_store.find("div", {"class": "street-address"}).stripped_strings))

                if soup_store.find("div", {"class": "span-15 omega location-title"}):
                    location_name = soup_store.find("div", {"class": "span-15 omega location-title"}).text

                if soup_store.find("span", {"class": "locality"}):
                    city = soup_store.find("span", {"class": "locality"}).text

                if soup_store.find("span", {"class": "region"}):
                    state = soup_store.find("span", {"class": "region"}).text

                if soup_store.find("span", {"class": "postal-code"}):
                    zipp = soup_store.find("span", {"class": "postal-code"}).text

                    ca_zip_list = re.findall(r'[A-Z]{1}[0-9]{1}[A-Z]{1}\s*[0-9]{1}[A-Z]{1}[0-9]{1}', str(zipp))
                    us_zip_list = re.findall(re.compile(r"\b[0-9]{5}(?:-[0-9]{4})?\b"), str(zipp))
                    if ca_zip_list:
                        country_code = "CA"

                    if us_zip_list:
                        country_code = "US"

                if soup_store.find("div", {"class": "field field-name-field-phone-number field-type-text field-label-inline clearfix"}):
                    phone_raw = soup_store.find("div", {
                        "class": "field field-name-field-phone-number field-type-text field-label-inline clearfix"}).text
                    phone_list = re.findall(re.compile(".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"), str(phone_raw))

                    if phone_list:
                        phone = phone_list[0]

                if soup_store.find("div", {"class": "field field-name-field-hours-of-operation field-type-table field-label-hidden"}):
                    hours_raw = soup_store.find("div", {
                        "class": "field field-name-field-hours-of-operation field-type-table field-label-hidden"})
                    if hours_raw:
                        hours_of_operation = " ".join(list(hours_raw.stripped_strings)[1:])

                latitude = soup_store.text.split('"latitude":"')[1].split('"')[0]
                longitude = soup_store.text.split('"longitude":"')[1].split('"')[0]

                store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                         store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]

                if str(store[1] + " "+ store[2]+ " "+ store[9]) not in addresses and country_code:
                    addresses.append(str(store[1] + " "+ store[2]+ " "+ store[9]))

                    store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in
                             store]

                    # print("data = " + str(store))
                    # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
                    yield store

            # print("cat_url next url == "+ str(soup_locations.find("a",{"title","Go to next page"})))
            if soup_locations.find("a", {"title": "Go to next page"}):
                cat_url = base_url + soup_locations.find("a", {"title": "Go to next page"})["href"]
                # print("next page")
            else:
                break


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
