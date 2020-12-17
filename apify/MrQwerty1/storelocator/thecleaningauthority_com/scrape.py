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
    s = set()
    url = "https://www.thecleaningauthority.com/"
    api_url = "https://www.thecleaningauthority.com/locations/"
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

    session = SgRequests()
    r = session.get(api_url)
    tree = html.fromstring(r.text)
    li = tree.xpath("//li[@class='item']")

    for l in li:
        locator_domain = url
        line = l.xpath(".//span[@class='address']/text()")
        line = ", ".join(list(filter(None, [l.strip() for l in line])))
        a = usaddress.tag(line, tag_mapping=tag)[0]
        street_address = f"{a.get('address1')} {a.get('address2') or ''}".strip()
        if street_address == "None":
            street_address = "<MISSING>"
        city = a.get("city") or "<MISSING>"
        state = a.get("state") or "<MISSING>"
        postal = a.get("postal") or "<MISSING>"
        country_code = "US"
        slug = "".join(l.xpath(".//strong[@class='name']/a/@href")).split("?")[0]
        store_number = (
            "".join(
                tree.xpath(
                    f"//li[@class='location' and @data-href='{slug}']/@data-loc-id"
                )
            )
            or "<MISSING>"
        )
        page_url = f"https://www.thecleaningauthority.com{slug}"
        location_name = "".join(l.xpath(".//strong[@class='name']/a/text()")).strip()
        phone = "".join(l.xpath(".//a[@class='number']/text()")).strip() or "<MISSING>"
        latitude = (
            "".join(
                tree.xpath(
                    f"//li[@class='location' and @data-href='{slug}']/@data-latitude"
                )
            )
            or "<MISSING>"
        )
        longitude = (
            "".join(
                tree.xpath(
                    f"//li[@class='location' and @data-href='{slug}']/@data-longitude"
                )
            )
            or "<MISSING>"
        )
        location_type = "<MISSING>"
        hours_of_operation = "<MISSING>"

        if store_number in s:
            continue

        s.add(store_number)
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
