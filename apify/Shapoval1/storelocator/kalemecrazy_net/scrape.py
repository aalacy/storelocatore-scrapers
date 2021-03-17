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
    locator_domain = "https://kalemecrazy.net"
    api_url = "https://kalemecrazy.net/locations/"
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
    block = tree.xpath("//div[./a[contains(text(), 'Visit')]]/preceding-sibling::div")
    for i in block:
        location_name = "".join(i.xpath(".//p[1]/text()"))

        ad = " ".join(i.xpath(".//p[2]/text()"))
        a = usaddress.tag(ad, tag_mapping=tag)[0]
        phone = "".join(i.xpath(".//a/text()")) or "<MISSING>"
        postal = a.get("postal") or "<MISSING>"
        city = a.get("city") or "<MISSING>"
        state = a.get("state") or "<MISSING>"
        country_code = "US"
        page_url = "".join(
            i.xpath('.//following-sibling::div/a[contains(text(), "Visit")]/@href')
        )
        session = SgRequests()
        r = session.get(page_url)
        trees = html.fromstring(r.text)
        street_address = (
            "".join(trees.xpath('//span[@itemprop="streetAddress"]/text()'))
            .replace(",", "")
            .replace("\n", "")
            or "<MISSING>"
        )
        if ad.find("MIAMI"):
            street_address = (
                f"{a.get('address1')} {a.get('address2')}".replace("None", "").strip()
                or "<MISSING>"
            )
        if location_name.find("MORNINGSIDE/HIGHLANDS") != -1:
            street_address = street_address.replace("30306", "")
        if city == "<MISSING>":
            city = (
                "".join(
                    trees.xpath('//span[@itemprop="addressLocality"]/text()')
                ).replace(",", "")
                or "<MISSING>"
            )
        if state == "<MISSING>":
            state = (
                "".join(
                    trees.xpath('//span[@itemprop="addressRegion"]/text()')
                ).replace(",", "")
                or "<MISSING>"
            )
        if postal == "<MISSING>":
            postal = (
                "".join(trees.xpath('//span[@itemprop="postalCode"]/text()')).replace(
                    ",", ""
                )
                or "<MISSING>"
            )
        if phone == "<MISSING>":
            phone = (
                "".join(trees.xpath('//span[@itemprop="telephone"]/text()')).replace(
                    ",", ""
                )
                or "<MISSING>"
            )
        store_number = "<MISSING>"
        latitude = (
            " ".join(trees.xpath('//meta[@itemprop="latitude"]/@content'))
            or "<MISSING>"
        )
        longitude = (
            " ".join(trees.xpath('//meta[@itemprop="longitude"]/@content'))
            or "<MISSING>"
        )
        location_type = "<MISSING>"
        hours_of_operation = (
            " ".join(trees.xpath('//meta[@itemprop="openingHours"]/@content'))
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
