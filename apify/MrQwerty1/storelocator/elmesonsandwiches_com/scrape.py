import csv
from urllib.parse import unquote
import json
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
    locator_domain = "https://www.elmesonsandwiches.com/"
    page_url = "https://www.elmesonsandwiches.com/restaurantes/"

    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)
    text = "".join(tree.xpath("//div/@data-elfsight-google-maps-options"))
    js = json.loads(unquote(text))["markers"]

    for j in js:
        phone_index = 0
        hours_index = 0
        cnt = 0
        description = j.get("infoDescription")
        if "Monday" not in description:
            continue
        root = html.fromstring(description)
        text = root.xpath(".//text()")
        for t in text:
            if "Phone" in t:
                phone_index = cnt
            if "Monday" in t:
                hours_index = cnt
            cnt += 1

        line = j.get("position")
        street_address, city, state, postal = get_address(line)
        country_code = "US"
        store_number = "<MISSING>"
        location_name = j.get("infoTitle")
        if phone_index != 0:
            phone = text[phone_index].replace("Phone:", "").strip()
        else:
            phone = "<MISSING>"
        latitude, longitude = j.get("coordinates").split(", ")
        location_type = "<MISSING>"
        if hours_index != 0:
            _tmp = []
            for t in text[hours_index:]:
                if "Drive" in t:
                    continue
                _tmp.append(t.strip())

            hours_of_operation = ";".join(_tmp)
        else:
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
