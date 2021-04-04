import csv
from sgrequests import SgRequests
import json
from sgscrape.sgpostal import parse_address_intl

from util import Util  # noqa: I900

myutil = Util()


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
    locator_domain = "https://www.lornajane.com/"
    base_url = "https://www.lornajane.com/on/demandware.store/Sites-LJUS-Site/en_US/Stores-FindStores?showMap=true&radius=15&selectedCountryCode=US&postalCode=&radius=300%20mi"
    r = session.get(base_url)
    items = json.loads(r.text)["stores"]
    data = []
    for item in items:
        page_url = "<MISSING>"
        location_name = item["name"]
        street_address = myutil._valid1(
            myutil._valid(f"{item['address1']}")
            + " "
            + myutil._valid1(item.get("address2", ""))
        ).replace("None", "")
        city = myutil._valid(item["city"])
        state = myutil._valid(item["stateCode"])
        zip = myutil._valid(myutil._digit(item["postalCode"]))
        raw_address = f"{street_address} {city}, {state} {zip}"
        addr = parse_address_intl(raw_address)
        country_code = item["countryCode"]
        store_number = item["ID"]
        phone = myutil._valid_phone(item.get("phone", ""))
        location_type = "<MISSING>"
        latitude = item["latitude"]
        longitude = item["longitude"]
        hours_of_operation = "<INACCESSIBLE>"
        if "storeHours" in item:
            if len(item["storeHours"].split("<br/>")) > 1:
                hours_of_operation = "; ".join(
                    myutil._strip_list(item["storeHours"].split("<br/>"))
                )
            else:
                hours_of_operation = "; ".join(
                    myutil._strip_list(item["storeHours"].split("<br />"))
                )

        _item = [
            locator_domain,
            page_url,
            location_name,
            addr.street_address_1,
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
        data.append(_item)

    return data


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
