import csv
import os
from sgselenium import SgSelenium
import re
import json

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


def rreplace(s, old, new, count):
    return (s[::-1].replace(old[::-1], new[::-1], count))[::-1]


def fetch_data():
    driver = SgSelenium().firefox()
    driver.get(
        'https://www.armani.com/experience/us/?yoox_storelocator_action=true&action=yoox_storelocator_get_all_stores')

    json_str = driver.find_element_by_tag_name('body').text
    dict_from_json = json.loads(json_str)
    for store_data in dict_from_json:
        store = []
        if "location" not in store_data:
            continue
        if store_data["wpcf-yoox-store-country-iso"].lower() != "us" and store_data["wpcf-yoox-store-country-iso"].lower() != "ca":
            continue
        store.append("https://www.armani.com")
        store.append(store_data["post_title"])
        address = rreplace(store_data["wpcf-yoox-store-address"],
                           store_data["location"]["city"]["name"], "", 1)
        street_address = " ".join(address.split("|")[:-1])
        store_zip = address.split("|")[-1].split(",")[0]
        store.append(street_address)
        store.append(store_data["location"]["city"]["name"])
        store.append(address.split(
            "|")[-1].split(",")[-1] if len(address.split("|")[-1].split(",")) == 3 else "<MISSING>")
        if "new york" in store[-2].lower():
            store[-1] = "NY"
        # if store[-1] in addresses:
        #     continue
        # addresses.append(store[-1])
        store.append(store_zip)
        store.append(store_data["wpcf-yoox-store-country-iso"].upper())
        if store[-1] == "US":
            zip_split = re.findall(r"\b[0-9]{5}(?:-[0-9]{4})?\b", store[-2])
            if zip_split:
                store[-2] = zip_split[-1]
        if store[-1] == "CA":
            if len(store[-2]) == 3:
                store[-3] = address.split("|")[-1].split(",")[-1].split(" ")[1]
                store[-2] = " ".join(address.split("|")
                                     [-1].split(",")[-1].split(" ")[2:])
        store.append(store_data["ID"])
        store.append(store_data["wpcf-yoox-store-phone"].replace("\xa0", "").split("Suggest")[0].split("|")[
                     0] if "wpcf-yoox-store-phone" in store_data and store_data["wpcf-yoox-store-phone"] else "<MISSING>")
        store.append(store_data["wpcf-store-main-store-brand"])
        store.append(store_data["_yoox-store-lat"])
        store.append(store_data["_yoox-store-lng"])
        store.append("<MISSING>")
        store.append(
            "https://www.armani.com/experience/us/store-locator/#store/"+str(store_data["ID"]))
        yield store
    driver.quit()


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
