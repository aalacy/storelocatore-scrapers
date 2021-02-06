import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from urllib.parse import urljoin
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

    locator_domain = "https://www.loscucos.com/"
    base_url = "https://www.loscucos.com/locations.html"
    rr = session.get(base_url)
    soup = bs(rr.text, "lxml")
    locations = soup.select(
        "div#bp_infinity div.grpelem div.Location-Buttons---Background a.Location-Buttons--Text--Glow---Black-100----Blur-10-copy"
    )
    for location in locations:
        page_url = urljoin("https://www.loscucos.com", location["href"])
        print(page_url)
        store_number = "<MISSING>"
        location_name = location.span.text
        country_code = "US"
        r1 = session.get(page_url)
        soup1 = bs(r1.text, "lxml")
        _name = location_name.split("@")[0].strip()
        name_tag = soup1.select_one("img.colelem", alt=_name)
        siblings = [_ for _ in name_tag.next_siblings if _.name]
        imgs = []
        for _ in siblings:
            if _.name == "img":
                imgs.append(_)
            else:
                imgs += _.find_all("img")

        street_address = ""
        city = ""
        state = ""
        zip = ""
        try:
            _address = imgs[0]["alt"]
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
            import pdb

            pdb.set_trace()
        phone = imgs[1]["alt"].split("Fax")[0].replace("Telephone:", "").strip()
        location_type = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        hours_of_operation = "; "
        try:
            _hours = imgs[2]["alt"].replace("Business Hours", "").strip().split(" ")
            hours = []
            hour = ""
            for _ in _hours:
                hour += _ + " "
                if _.endswith("PM"):
                    hours.append(hour.strip())
                    hour = ""

            hours_of_operation = "; ".join(hours)
        except:
            import pdb

            pdb.set_trace()

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
