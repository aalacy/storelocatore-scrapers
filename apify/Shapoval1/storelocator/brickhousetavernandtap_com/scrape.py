import csv
import usaddress
from lxml import html
from sgrequests import SgRequests


def write_output(data):
    with open("data.csv", mode="w", encoding="utf8", newline="") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

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

        for row in data:
            writer.writerow(row)


def fetch_data():
    out = []
    locator_domain = "https://www.brickhousetavernandtap.com"
    page_url = "https://www.brickhousetavernandtap.com/locations"
    session = SgRequests()
    tag = {
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
        "ZipCode": "postal",
    }
    r = session.get(page_url)
    tree = html.fromstring(r.text)
    block = tree.xpath('//li[@style="height: 723px"]')
    for b in block:

        location_name = "".join(b.xpath(".//h2/a/text()")).replace("*", "")
        line = b.xpath(".//p[./br]/text()")
        line = list(filter(None, [a.strip() for a in line]))
        line = " ".join(line).split("Store")[0].strip()
        a = usaddress.tag(line, tag_mapping=tag)[0]

        street_address = f"{a.get('address1')} {a.get('SecondStreetName')} {a.get('SecondStreetNamePostType')} {a.get('address2')}".replace(
            "None", ""
        ).strip()
        phone = "".join(b.xpath('.//a[contains(@href, "tel")]/text()'))
        if phone.find("GrubhubUberEats") != -1:
            phone = phone.split("GrubhubUberEats")[0]
        city = a.get("city")
        state = a.get("state")
        country_code = "US"
        store_number = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        location_type = "<MISSING>"
        hours_of_operation = b.xpath(".//p[1]/following-sibling::p//text()")
        hours_of_operation = list(filter(None, [a.strip() for a in hours_of_operation]))
        hours_of_operation = (
            " ".join(hours_of_operation)
            .split("Store Hours:")[1]
            .split("Happy Hour:")[0]
            .strip()
        )

        postal = a.get("postal")
        row = [
            locator_domain,
            page_url,
            location_name,
            street_address,
            city,
            state,
            postal,
            country_code,
            store_number,
            phone,
            location_type,
            latitude,
            longitude,
            hours_of_operation,
        ]
        out.append(row)

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
