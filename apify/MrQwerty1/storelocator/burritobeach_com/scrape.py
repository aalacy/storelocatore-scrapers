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


def get_coords():
    coords = []
    session = SgRequests()
    r = session.get(
        "https://www.google.com/maps/d/u/0/kml?mid=1K5owjFYA9Cmw-5LeqANVtvPEqzM&forcekml=1"
    )
    tree = html.fromstring(r.content)
    markers = tree.xpath("//coordinates/text()")
    for m in markers:
        m = m.replace(",0", "")
        lng, lat = m.split(",")
        coords.append((lat.strip(), lng.strip()))

    return coords


def get_address(line):
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
        "OccupancyType": "address2",
        "OccupancyIdentifier": "address2",
        "SubaddressIdentifier": "address2",
        "SubaddressType": "address2",
        "PlaceName": "city",
        "StateName": "state",
        "ZipCode": "postal",
    }

    a = usaddress.tag(line, tag_mapping=tag)[0]
    street_address = f"{a.get('address1')} {a.get('address2') or ''}".strip()
    if street_address == "None":
        street_address = "<MISSING>"
    city = a.get("city") or "<MISSING>"
    state = a.get("state") or "<MISSING>"
    postal = a.get("postal") or "<MISSING>"

    return street_address, city, state, postal


def fetch_data():
    out = []
    locator_domain = "https://burritobeach.com/"
    page_url = "https://burritobeach.com/locations"

    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    divs = tree.xpath(
        "//div[@class='location-div' and not(.//a[contains(@href, 'mailto')])]"
    )
    coords = get_coords()

    for d in divs:
        location_name = "".join(d.xpath(".//h2/text()")).strip()
        line = "".join(
            d.xpath(".//p[./span[@class='fa fa-map-marker']][1]/text()")
        ).strip()
        street_address, city, state, postal = get_address(line)
        country_code = "US"
        store_number = "<MISSING>"
        phone = (
            "".join(d.xpath(".//p[./span[@class='fa fa-phone']]/text()"))
            .replace("P:", "")
            .strip()
            or "<MISSING>"
        )
        latitude, longitude = coords.pop(0)
        location_type = "<MISSING>"

        hours = d.xpath(".//p[./span[@class='fa fa-clock-o']]/text()")
        hours = list(
            filter(
                None,
                [h.replace("amâ", " - ").replace("Hours", "").strip() for h in hours],
            )
        )
        hours_of_operation = ";".join(hours) or "<MISSING>"
        if "closed" in hours_of_operation:
            hours_of_operation = "Closed"

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
