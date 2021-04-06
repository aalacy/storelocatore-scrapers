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

    locator_domain = "https://www.angrycrabshack.com"

    api_url = "https://www.angrycrabshack.com/locations"
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
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    block = tree.xpath('//div[./p[@class="webpage"]]')
    for b in block:

        slug = "".join(b.xpath('.//a[contains(text(), "Webpage")]/@href'))
        page_url = f"{locator_domain}{slug}"
        session = SgRequests()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)
        location_name = (
            "".join(tree.xpath("//h1/text()"))
            + "".join(tree.xpath('//h3[@class="alt slider"]/text()'))
            .replace("  ", " ")
            .replace("\n", "")
            .strip()
        )
        adr = (
            " ".join(
                tree.xpath(
                    '//h3[contains(text(), "Address")]/following-sibling::p[1]/text()'
                )
            )
            .replace("\n", "")
            .strip()
        )
        a = usaddress.tag(adr, tag_mapping=tag)[0]
        location_type = "<MISSING>"
        street_address = f"{a.get('address1')} {a.get('address2')}".replace(
            "None", ""
        ).strip()
        text = "".join(tree.xpath('//iframe[@loading="lazy"]/@data-lazy-src'))
        latitude = text.split("!3d")[1].strip().split("!")[0].strip()
        longitude = text.split("!2d")[1].strip().split("!")[0].strip()
        country_code = "US"
        state = a.get("state")
        postal = a.get("ZipCode")
        city = a.get("city")
        store_number = "<MISSING>"
        hours_of_operation = (
            " ".join(
                tree.xpath(
                    '//h3[contains(text(), "Hours")]/following-sibling::p/text()'
                )
            )
            .replace("\n", "")
            .strip()
        )
        phone = (
            " ".join(
                tree.xpath(
                    '//h3[contains(text(), "Address")]/following-sibling::p/a/text()'
                )
            )
            or "<MISSING>"
        )

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
