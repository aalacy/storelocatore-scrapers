import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import usaddress
import json

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
    data = []

    locator_domain = "https://www.cafishgrill.com/"
    base_url = "https://www.cafishgrill.com/pages/stores-json"
    r = session.get(base_url)
    soup = bs(r.text, "lxml")
    scripts = json.loads(soup.find("script", id="StoreJSON").string)["stores"]
    for script in scripts:
        page_url = "<MISSING>"
        store_number = script["uuid"]
        location_name = script["Fcilty_nam"]
        address = usaddress.tag(
            script["Locality"],
            tag_mapping={
                "Recipient": "recipient",
                "AddressNumber": "address1",
                "AddressNumberPrefix": "address1",
                "AddressNumberSuffix": "address1",
                "StreetName": "address1",
                "StreetNamePreDirectional": "address1",
                "StreetNamePreModifier": "address1",
                "StreetNamePreType": "address1",
                "StreetNamePostDirectional": "address1",
                "StreetNamePostModifier": "address1",
                "StreetNamePostType": "address1",
                "CornerOf": "address1",
                "IntersectionSeparator": "address1",
                "LandmarkName": "address1",
                "USPSBoxGroupID": "address1",
                "USPSBoxGroupType": "address1",
                "USPSBoxID": "address1",
                "USPSBoxType": "address1",
                "BuildingName": "address2",
                "OccupancyType": "address2",
                "OccupancyIdentifier": "address2",
                "SubaddressIdentifier": "address2",
                "SubaddressType": "address2",
                "PlaceName": "city",
                "StateName": "state",
                "ZipCode": "zip_code",
            },
        )
        city = address[0]["city"]
        state = address[0]["state"]
        street_address = address[0]["address1"] + myutil._valid1(
            address[0].get("address2", "")
        )
        zip = address[0]["zip_code"]
        country_code = "US"
        phone = myutil._valid(script.get("Phone_number", ""))
        location_type = "<MISSING>"
        latitude = myutil._valid(script["Ycoord"])
        longitude = myutil._valid(script["Xcoord"])
        soup1 = bs(script["Street_add"], "lxml")
        hours = []
        _hours = soup1.select("span")
        if len(_hours) > 1:
            x = 0
            while x < len(_hours):
                hours.append(f"{_hours[x].text}:{_hours[x+1].text}")
                x += 2

        hours_of_operation = myutil._valid("; ".join(hours))
        if script["Fax_number"] == "COMING SOON":
            hours_of_operation = "COMING SOON"

        _item = [
            locator_domain,
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

        data.append(_item)

    return data


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
