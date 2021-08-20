import csv
import json

from bs4 import BeautifulSoup

from sgrequests import SgRequests


session = SgRequests()


def write_output(data):
    with open("data.csv", mode="w") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

        # Header
        writer.writerow(
            [
                "locator_domain",
                "location_name",
                "street_address",
                "city",
                "state",
                "zip",
                "country_code",
                "store_number",
                "phone",
                "location_type",
                "latitude",
                "longitude",
                "hours_of_operation",
                "page_url",
            ]
        )
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    }
    r = session.get(
        "https://maps.savers.com/api/getAsyncLocations?template=search&level=search&radius=1000000000&search=11756",
        headers=headers,
    )
    return_main_object = []
    location_list = r.json()["markers"]
    for store_data in location_list:
        store_details = json.loads(BeautifulSoup(store_data["info"], "lxml").text)
        link = store_details["url"]
        if "savers-thrift" not in link:
            continue
        store = []
        store.append("https://www.savers.com")
        store.append(store_details["location_name"])
        store.append(
            (store_details["address_1"] + " " + store_details["address_2"]).strip()
        )
        store.append(store_details["city"])
        store.append(store_details["region"])
        store.append(store_details["post_code"])
        store.append(store_details["country"])
        store.append(store_data["locationId"])
        location_request = session.get(link, headers=headers)
        location_soup = BeautifulSoup(location_request.text, "lxml")
        store.append(location_soup.find(alt="Call Store").text.strip())
        store.append(location_soup.find(class_="location-logo")["data-brand"])
        store.append(store_data["lat"])
        store.append(store_data["lng"])
        store.append(
            " ".join(
                list(location_soup.find("div", {"class": "hours"}).stripped_strings)
            )
        )
        store.append(link)
        return_main_object.append(store)
    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
