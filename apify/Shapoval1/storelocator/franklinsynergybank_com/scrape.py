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

    locator_domain = "https://www.firstbankonline.com/"
    api_url = "https://www.firstbankonline.com/location-sitemap.xml"
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
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
    }

    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.content)
    div = tree.xpath("//url/loc")
    for d in div:

        page_url = "".join(d.xpath(".//text()"))
        if page_url == "https://www.firstbankonline.com/location/":
            continue
        session = SgRequests()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)

        location_name = "".join(tree.xpath('//h2[@class="lightblue h3"]/text()'))
        location_type = "Branch"
        ad = (
            " ".join(tree.xpath('//p[@class="address"]/text()'))
            .replace("\r\n", "")
            .strip()
        )
        a = usaddress.tag(ad, tag_mapping=tag)[0]

        street_address = f"{a.get('address1')} {a.get('address2')}".replace(
            "None", ""
        ).strip()
        state = a.get("state") or "<MISSING>"
        postal = a.get("postal") or "<MISSING>"
        country_code = "US"
        service = (
            " ".join(tree.xpath('//div[@class="services col"]/span/text()'))
            .replace("\r\n", "")
            .strip()
        )
        if "Branch" not in service:
            continue
        city = a.get("city") or "<MISSING>"
        store_number = "<MISSING>"
        latitude = (
            "".join(tree.xpath('//script[contains(text(), "branch_locations")]/text()'))
            .split("] = new google.maps.LatLng(")[1]
            .split(",")[0]
            .strip()
        )
        longitude = (
            "".join(tree.xpath('//script[contains(text(), "branch_locations")]/text()'))
            .split("] = new google.maps.LatLng(")[1]
            .split(",")[1]
            .split(")")[0]
            .strip()
        )
        phone = (
            "".join(tree.xpath('//a[contains(@href, "tel")]/text()'))
            .replace("Call", "")
            .strip()
            or "<MISSING>"
        )
        hours_of_operation = (
            " ".join(tree.xpath('//div[@class="hrs"]/p//text()'))
            .replace("\r\n", "")
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
        if hours_of_operation == "<MISSING>":
            hours_of_operation = (
                " ".join(
                    tree.xpath(
                        '//h4[text()="Drive-Through Hours"]/preceding-sibling::p//text()'
                    )
                )
                .replace("\r\n", "")
                .replace("\n", "")
                .strip()
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
