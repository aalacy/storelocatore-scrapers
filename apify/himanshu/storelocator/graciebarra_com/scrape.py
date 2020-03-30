import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json



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
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
        "X-Requested-With": "XMLHttpRequest",
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Accept": "application/json, text/plain, */*",
        "X-Knack-Application-Id": "5bc58e7736d50c7fd1d9406d",
        "X-Knack-REST-API-Key": "renderer"
    }
    r = session.get("https://us-east-1-renderer-read.knack.com/v1/scenes/scene_1/views/view_1/records?format=both&page=1&rows_per_page=10000&filters=%7B%22rules%22%3A%5B%7B%22field%22%3A%22field_3%22%2C%22operator%22%3A%22near%22%2C%22value%22%3A%2211756+Spring+Club+Drive%2C+San+Antonio%2C+TX%2C+USA%22%2C%22units%22%3A%22miles%22%2C%22range%22%3A%22100000%22%7D%5D%2C%22match%22%3A%22and%22%7D", headers=headers)
    data = r.json()["records"]
    # print(data)
    for store_data in data:
        if store_data["field_3_raw"]["country"].lower() not in ("united states", "canada"):
            continue
        store = []
        store.append("https://graciebarra.com")
        store.append(store_data["field_1_raw"])
        store.append(store_data["field_3_raw"]["street"]
                     if store_data["field_3_raw"]["street"] else "<MISSING>")
        if "Coming Soon" in store[-1]:
            continue
        if "street2" in store_data["field_3_raw"]:
            store[-1] = store[-1] + " " + store_data["field_3_raw"]["street2"]
        if "USA" in store[-1]:
            store[-1] = store[-1].split(",")[0]
        # there were special cases with CA so i had to put this condition here
        if "CA" in store[-1]:
            store[-1] = store[-1].replace("CA", "").split(",")[0]
        if store_data["field_3_raw"]["city"]:
            city = store_data["field_3_raw"]["city"].split(",")[0]
        else:
            city = "<MISSING>"
        if store_data["field_3_raw"]["state"]:
            state = store_data["field_3_raw"]["state"]
        else:
            state = "<MISSING>"
        if " Sugarland" in state:
            state = "Texas"
            city = "Sugarland"

        # splitting street address with city and getting 0 element

        store.append(city if city else "<MISSING>")
        store.append(state if state else "<MISSING>")
        # This was a special case in which websie had miami and florida as state

        if "Florida" in store[-1]:
            store[-1] = "Florida"
        store.append(store_data["field_3_raw"]["zip"]
                     if store_data["field_3_raw"]["zip"] else "<MISSING>")
        store.append("US" if store_data["field_3_raw"]["country"].lower(
        ) == "united states" else "CA")
        store.append("<MISSING>")
        store.append(store_data["field_4_raw"]["number"]
                     if store_data["field_4_raw"] else "<MISSING>")
        store.append("<MISSING>")
        store.append(store_data["field_3_raw"]["latitude"])
        store.append(store_data["field_3_raw"]["longitude"])
        page_url = store_data["field_5_raw"]["url"]
        # print(page_url)
        # if "" == page_url:
        #     page_url = "<MISSING>"
        # print(page_url)
        store.append("<MISSING>")

        store.append("<MISSING>")
        store = [str(x).encode('ascii', 'ignore').decode(
            'ascii').strip() if x else "<MISSING>" for x in store]
        # print("data == " + str(store))
        # print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
