import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
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


def parse_detail(data, base_url, locator_domain, country):
    rr = session.get(base_url)
    soup = bs(rr.text, "lxml")
    locations = soup.select("ul.st-shortcuts--list li ul li a")
    for location in locations:
        page_url = location["href"]
        rr1 = session.get(page_url)
        soup1 = bs(rr1.text, "lxml")
        store_number = page_url.split("sid=")[1]
        location_name = myutil._valid(location.text)
        country_code = country
        street_address = ""
        city = ""
        state = "<MISSING>"
        zip = ""
        address = soup1.select_one("div.store-details a.store-address address.address")
        if not address:
            continue
        address = myutil._strip_list(
            soup1.select_one(
                "div.store-details a.store-address address.address"
            ).text.split("\n")
        )
        zip = myutil._valid(address[-1])
        if country == "US":
            try:
                _address = " ".join(
                    soup1.select_one(
                        "div.store-details a.store-address address.address"
                    ).text.split("\n")
                ).strip()
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
                    myutil._valid1(address[0].get("address1"))
                    + " "
                    + myutil._valid1(address[0].get("address2"))
                )
                city = myutil._valid(address[0].get("city")).replace(",", "")
                state = myutil._valid(address[0].get("state"))
            except:
                city = myutil._valid(address[-2]).replace(",", "")
                street_address = " ".join(address[:-2])
        else:
            street_address = " ".join(address[:-2])
            city = myutil._valid(address[-2]).replace(",", "")
            state = "<MISSING>"

        _phone = soup1.select_one("div.store-details a.phone")
        phone = "<MISSING>"
        if _phone:
            phone = myutil._valid(_phone["href"].replace("tel:", ""))
        location_type = "<MISSING>"
        hours = []
        for _ in soup1.select("#store-hours div.store-hour-box"):
            hours.append(f'{_.h5.text.strip()}: {_.select_one("span").text.strip()}')
        hours_of_operation = myutil._valid("; ".join(hours))
        latitude = soup1.select_one(".map-canvas")["data-latitude"]
        longitude = soup1.select_one(".map-canvas")["data-longitude"]

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

        myutil._check_duplicate_by_loc(data, _item)

    return data


def fetch_data():
    data = []

    # canada
    locator_domain = "https://ca.diesel.com/"
    base_url = "https://ca.diesel.com/en/stores"
    parse_detail(data, base_url, locator_domain, "CA")

    # uk
    locator_domain = "https://uk.diesel.com/"
    base_url = "https://uk.diesel.com/en/stores"
    parse_detail(data, base_url, locator_domain, "UK")

    # us
    locator_domain = "https://shop.diesel.com/"
    base_url = "https://shop.diesel.com/en/stores"
    parse_detail(data, base_url, locator_domain, "US")

    return data


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
