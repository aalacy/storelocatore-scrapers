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
    locator_domain = "http://kindersmeats.com/"
    api_url = "http://kindersmeats.com/locations.php"
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
    r = session.get(api_url)
    tree = html.fromstring(r.text)
    block = tree.xpath('//div[@class="storeListing"]')

    for b in block:

        line = b.xpath('.//div[@class="storeListingDetails"]/text()')
        line = list(filter(None, [a.strip() for a in line]))
        line = " ".join(line).split("(")[0].strip()
        a = usaddress.tag(line, tag_mapping=tag)[0]
        location_name = "".join(b.xpath(".//a/strong/text()"))
        street_address = f"{a.get('address1')} {a.get('address2')}".replace(
            "None", ""
        ).strip()
        phone = (
            "".join(b.xpath('.//a[contains(@href, "tel")]/@href'))
            .split("tel:")[1]
            .strip()
        )
        city = a.get("city")
        state = a.get("state")
        postal = a.get("postal")
        country_code = "US"
        store_number = "<MISSING>"
        slug = "".join(b.xpath(".//a[./strong]/@href"))
        page_url = f"{locator_domain}{slug}"
        session = SgRequests()
        r = session.get(page_url)
        trees = html.fromstring(r.text)
        ll = "".join(trees.xpath("//iframe/@src")).split("&ll=")[1].split("&")[0]
        latitude = ll.split(",")[0]
        longitude = ll.split(",")[1]
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
