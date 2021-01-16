import csv
import json
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
                "page_url",
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
    base_url = "https://www.smiggle.co.uk"
    headers = {}
    res = session.get(
        "https://www.smiggle.co.uk/shop/en/smiggleuk/stores/gb/gball", headers=headers
    )

    store_list = json.loads(
        res.text.split('<div id="storeSelection" style="display: none">')[1]
        .split("</div")[0]
        .replace("\n", "")
        .replace("\t", "")
        .replace("\r", "")
    )["storeLocator"]

    data = []

    for store in store_list:
        page_url = store["storeURL"]
        country_code = store["country"]

        if country_code != "GB":
            continue

        location_name = store["storeName"]
        shop_address = store["shopAddress"].replace("&amp;", "&").replace("&#039;", "'")
        shop_address = "" if shop_address == "." or shop_address == "" else shop_address
        street_address = (
            store["streetAddress"].replace("&amp;", "&").replace("&#039;", "'")
        )
        street_address = (
            "" if street_address == "." or street_address == "" else street_address
        )
        if shop_address != "":
            street_address = (
                shop_address
                if street_address == ""
                else shop_address + ", " + street_address
            )
        city = store["city"].replace("&amp;", "&").replace("&#039;", "'")
        zip = store["zipcode"].strip()
        zip = "<MISSING>" if zip == "." or zip == "" else zip
        state = store["state"].strip()
        latitude = store["latitude"]
        longitude = store["longitude"]
        store_number = store["locId"]
        location_type = "<MISSING>"
        phone = store["phone"].strip()
        phone = "<MISSING>" if phone == "" else phone
        hours_of_operation = store["storehours"].strip()
        hours_of_operation = (
            "<MISSING>" if hours_of_operation == "" else hours_of_operation
        )

        data.append(
            [
                base_url,
                page_url,
                location_name,
                street_address,
                city,
                state,
                '="' + zip + '"',
                country_code,
                store_number,
                '="' + phone + '"',
                location_type,
                latitude,
                longitude,
                hours_of_operation,
            ]
        )

    return data


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
