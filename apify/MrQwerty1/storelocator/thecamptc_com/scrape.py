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
        "BuildingName": "address2",
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
    locator_domain = "https://thecamptc.com/"
    api_url = "https://thecamptc.com/locator/index.php?controller=pjFront&action=pjActionGenerateXml&lat=34.0122346&lng=-117.688944&radius=5000&distance=miles&category_id=&filter_id="

    session = SgRequests()
    r = session.get(api_url)
    js = r.json()

    for j in js:
        location_name = j.get("name")
        source = j.get("marker_content")
        if not source:
            continue

        tree = html.fromstring(source)
        line = "".join(
            tree.xpath(
                "//dt[contains(text(), 'Address')]/following-sibling::dd[1]/text()"
            )
        )

        street_address, city, state, postal = get_address(line)
        if "," in state:
            state = state.split(",")[-1].strip()

        if city == "<MISSING>" and state == "<MISSING>":
            continue

        if state == "<MISSING>" and "," in city:
            state = city.split(",")[-1].strip()
            city = city.split(",")[0].strip()

        country_code = "US"
        store_number = "<MISSING>"
        page_url = (
            "".join(tree.xpath("//a[contains(@href, '/locations/')]/@href"))
            or "<MISSING>"
        )
        phone = (
            "".join(
                tree.xpath(
                    "//dt[contains(text(), 'Phone')]/following-sibling::dd[1]/text()"
                )
            )
            or "<INACCESSIBLE>"
        )
        if phone == "(213) 747-0655":
            phone = "(310) 294-2189"
        latitude = j.get("lat") or "<MISSING>"
        longitude = j.get("lng") or "<MISSING>"
        location_type = "<MISSING>"
        hours_of_operation = "<MISSING>"

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
