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

    locator_domain = "https://theyard.com/"
    api_url = "https://theyard.com/new-york-city-coworking-office-space/"
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
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath(
        '//a[text()="Locations"]/following-sibling::ul/li/a/following-sibling::ul/li/a'
    )
    for d in div:

        page_url = "".join(d.xpath(".//@href"))
        location_name = "".join(d.xpath(".//text()"))
        session = SgRequests()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)

        ad = (
            "".join(tree.xpath('//div[@class="address"]/p/text()[1]'))
            .replace("\n", "")
            .replace(", United States", "")
            .replace(", USA", "")
            .strip()
        )
        a = usaddress.tag(ad, tag_mapping=tag)[0]
        street_address = f"{a.get('address1')} {a.get('address2')}".replace(
            "None", ""
        ).strip()
        state = a.get("state") or "<MISSING>"
        postal = a.get("postal") or "<MISSING>"
        country_code = "USA"
        city = a.get("city") or "<MISSING>"
        location_type = "<MISSING>"
        store_number = "<MISSING>"
        phone = "<MISSING>"
        hoo = tree.xpath('//div[@class="address"]/p//text()')
        hoo = list(filter(None, [a.strip() for a in hoo]))
        hours_of_operation = " ".join(hoo[1:])

        session = SgRequests()
        r = session.get(
            "https://theyard.com/new-york-city-coworking-office-space/", headers=headers
        )
        tree = html.fromstring(r.text)
        latitude = (
            "".join(
                tree.xpath(f'//li[@data-display-name="{location_name}"]/@data-map-lat')
            )
            or "<MISSING>"
        )
        longitude = (
            "".join(
                tree.xpath(f'//li[@data-display-name="{location_name}"]/@data-map-lng')
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
