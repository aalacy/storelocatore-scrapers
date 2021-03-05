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
    base_url = "https://www.crewclothing.co.uk"
    res = session.get(
        "https://www.crewclothing.co.uk/customer-services/stores/",
    )
    store_list = json.loads(
        res.text.split("var myStores = ")[1].split(";</script>")[0]
    )["stores"]
    data = []

    for store in store_list:
        location_name = store["name"]
        city = store["town"]
        state = "<MISSING>"
        page_url = store["storeLink"]
        street_address = store["address1"]
        zip = store["postcode"].strip()
        country_code = store["country"] or "<MISSING>"
        phone = store["storecontacts"] or "<MISSING>"
        store_number = store["id"]
        location_type = store["storeType"]
        latitude = store["pca_wgs84_latitude"]
        longitude = store["pca_wgs84_longitude"]
        hours = (
            store["openinghours"].split("<br />")[1:]
            if "Collect" in store["openinghours"]
            else store["openinghours"].split("<br />")
        )
        hours = [x for x in hours if x]
        hours_of_operation = (
            " ".join(hours).replace("<BR>", " ").replace("<br>", " ").replace("–", "-")
            or "<MISSING>"
        )

        data.append(
            [
                base_url,
                page_url,
                location_name,
                street_address,
                city,
                state,
                zip,
                country_code,
                store_number,
                phone,
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
