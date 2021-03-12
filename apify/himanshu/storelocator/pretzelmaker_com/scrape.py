import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
from sgscrape.sgpostal import parse_address, International_Parser
import json


session = SgRequests()


def write_output(data):
    with open("data.csv", mode="w", encoding="utf-8") as output_file:
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
            ]
        )
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36",
        "content-type": "application/x-www-form-urlencoded",
    }
    data = "locateStore=true&country=USA"
    r = session.post("https://pretzelmaker.com/locations/", headers=headers, data=data)
    soup = BeautifulSoup(r.text, "lxml")
    return_main_object = []
    for script in soup.find_all("script"):
        content = script.string

        if content and "var stores = " in content:
            location_list = json.loads(
                content.split("var stores = ")[1].split("}];")[0] + "}]"
            )
            for store_data in location_list:
                store = []
                store.append("https://pretzelmaker.com")
                store.append(store_data["sl_name"])
                if any(
                    not store_data[i]
                    for i in ["sl_address", "sl_city", "sl_state", "sl_zip"]
                ):
                    raw_addr = []
                    for i in ["sl_address", "sl_city", "sl_state", "sl_zip"]:
                        if store_data[i]:
                            raw_addr.append(store_data[i])
                    raw_addr = " ".join(raw_addr)
                    nice = parse_address(International_Parser(), raw_addr)
                    store_data["sl_address"] = nice.street_address_1
                    if nice.street_address_2:
                        store_data["sl_address"] = (
                            store_data["sl_address"] + ", " + nice.street_address_2
                        )

                    store_data["sl_city"] = nice.city if nice.city else "<MISSING>"
                    store_data["sl_state"] = nice.state if nice.state else "<MISSING>"
                    store_data["sl_zip"] = (
                        nice.postcode if nice.postcode else "<MISSING>"
                    )
                store.append(store_data["sl_address"])
                store.append(store_data["sl_city"])
                store.append(store_data["sl_state"])
                store.append(store_data["sl_zip"])
                store.append("US")
                store.append(store_data["sl_id"])
                if not store_data["sl_phone"]:
                    store_data["sl_phone"] = "<MISSING>"
                store.append(
                    store_data["sl_phone"]
                    if store_data["sl_phone"] != "*" and store_data["sl_phone"] != "TBD"
                    else "<MISSING>"
                )
                store.append("pretzel maker")
                store.append(store_data["sl_latitude"])
                store.append(store_data["sl_longitude"])
                store.append("<MISSING>")
                for i in store:
                    if not i:
                        i = "<MISSING>"
                return_main_object.append(store)

    data = "locateStore=true&country=Canada"
    r = session.post("https://pretzelmaker.com/locations/", headers=headers, data=data)
    soup = BeautifulSoup(r.text, "lxml")
    for script in soup.find_all("script"):
        content = script.string
        if content and "var stores = " in content:
            location_list = json.loads(
                content.split("var stores = ")[1].split("}];")[0] + "}]"
            )
            for store_data in location_list:
                store = []
                store.append("https://pretzelmaker.com")
                store.append(store_data["sl_name"])
                if any(
                    not store_data[i]
                    for i in ["sl_address", "sl_city", "sl_state", "sl_zip"]
                ):
                    raw_addr = []
                    for i in ["sl_address", "sl_city", "sl_state", "sl_zip"]:
                        if store_data[i]:
                            raw_addr.append(store_data[i])
                    raw_addr = " ".join(raw_addr)
                    nice = parse_address(International_Parser(), raw_addr)

                    store_data["sl_address"] = nice.street_address_1
                    if nice.street_address_2:
                        store_data["sl_address"] = (
                            store_data["sl_address"] + ", " + nice.street_address_2
                        )

                    store_data["sl_city"] = nice.city if nice.city else "<MISSING>"
                    store_data["sl_state"] = nice.state if nice.state else "<MISSING>"
                    store_data["sl_zip"] = (
                        nice.postcode if nice.postcode else "<MISSING>"
                    )
                store.append(store_data["sl_address"])
                store.append(store_data["sl_city"])
                store.append(store_data["sl_state"])
                store.append(store_data["sl_zip"])
                store.append("CA")
                store.append(store_data["sl_id"])
                if not store_data["sl_phone"]:
                    store_data["sl_phone"] = "<MISSING>"
                store.append(
                    store_data["sl_phone"]
                    if store_data["sl_phone"] != "*" and store_data["sl_phone"] != "TBD"
                    else "<MISSING>"
                )
                store.append("pretzel maker")
                store.append(store_data["sl_latitude"])
                store.append(store_data["sl_longitude"])
                store.append("<MISSING>")
                for i in store:
                    if not i:
                        i = "<MISSING>"
                yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
