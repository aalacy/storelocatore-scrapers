import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from urllib.parse import urljoin
import json
import usaddress

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

    locator_domain = "https://us.fatface.com/"
    base_url = "https://us.fatface.com/stores"
    r = session.get(base_url)
    soup = bs(r.text, "lxml")
    links = soup.select("a.b-find-a-store-noresult__letter-store")
    for link in links:
        page_url = urljoin(
            "https://us.fatface.com",
            f"{link['href']}",
        )
        r1 = session.get(page_url)
        soup = bs(r1.text, "lxml")
        location = json.loads(
            soup.select_one("div.js-map-wrapper.b-find-a-store-map")["data-mapconfig"]
        )
        location_name = location["name"]
        store_number = location["id"]
        _address = f'{location["address1"]} {myutil._valid1(location.get("address2", ""))} {location["city"]}, {location["state"]} {location["postalCode"]} {location["countryCode"]}'
        street_address = (
            f'{location["address1"]} {myutil._valid1(location.get("address2", ""))}'
        )
        city = location["city"]
        state = soup.select_one('span[itemprop="addressLocality"]').text
        country_code = location["countryCode"] or "US"
        try:
            address = usaddress.tag(
                _address,
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
            street_address = (
                address[0]["address1"]
                + " "
                + myutil._valid1(address[0].get("address2", ""))
            )
            city = myutil._valid(address[0]["city"])
            zip = myutil._valid(address[0]["zip_code"])
            state = (
                myutil._valid(address[0].get("state", ""))
                .replace("None", "")
                .replace(",", "")
            )
        except:
            pass

        _zip = ""
        for _ in zip:
            if _.isdigit():
                _zip += _

        zip = _zip

        phone = myutil._valid(location["phone"])
        location_type = "<MISSING>"
        latitude = location["latitude"]
        longitude = location["longitude"]
        hours_of_operation = "; ".join(
            [
                _["content"]
                for _ in soup.select("ul.b-store-locator-details__listing li")
            ]
        )

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
