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
    base_url = "https://www.getitnowstores.com/"
    res = session.get(
        "https://www.getitnowstores.com/-/custom/GetStoresWithZipCode.json",
    )
    data = []
    store_list = json.loads(res.text)
    for store in store_list:
        if store["RelatedWebsite"] != "getitnowstores.com":
            continue
        page_url = "<MISSING>"
        location_name = "<MISSING>"
        street_address = store["Address1"]
        store_number = store["StoreNumber"]
        city = store["City"]
        state = store["State"]
        zip = store["ZipCode"]
        hours_of_operation = ""
        hours_of_operation += store["StoreHours1"] + " "
        hours_of_operation += store["StoreHours2"] + " "
        hours_of_operation += store["StoreHours3"] + " "
        hours_of_operation += store["StoreHours4"] + " "
        hours_of_operation += store["StoreHours5"]
        hours_of_operation = hours_of_operation.strip()
        country_code = "US"
        phone = store["PhoneNumber"]
        location_type = "<MISSING>"
        latitude = store["Latitude"]
        longitude = store["Longitude"]

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
