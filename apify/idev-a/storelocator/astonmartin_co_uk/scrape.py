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
    base_url = "https://astonmartin.co.uk"
    res = session.get(
        "https://astonmartin.co.uk/api/v1/dealers?latitude=51.5113555&longitude=-0.1568901000000551&cultureName=en-GB&take=26"
    )
    store_list = json.loads(res.text)
    data = []
    for store in store_list:
        if store["Address"]["CountryCode"] != "United Kingdom":
            continue
        page_url = (
            base_url + store["DealerPageUrl"]
            if store["DealerPageUrl"] is not None
            else "<MISSING>"
        )
        location_name = store["Name"] or "<MISSING>"
        street_address = store["Address"]["Street"] or "<MISSING>"
        city = store["Address"]["City"] or "<MISSING>"
        state = store["Address"]["StateCode"] or "<MISSING>"
        zip = store["Address"]["Zip"] or "<MISSING>"
        phone = store["PhoneNumber"]
        country_code = store["Address"]["CountryCode"] or "<MISSING>"
        store_number = store["DCSId"]
        location_type = "<MISSING>"
        latitude = store["Address"]["Latitude"] or "<MISSING>"
        longitude = store["Address"]["Longitude"] or "<MISSING>"
        hours = store["OpeningHours"]
        hours_of_operation = ""
        for x in hours:
            hours_of_operation += x + " "
        hours_of_operation = hours_of_operation.replace("–", "-").strip()

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
