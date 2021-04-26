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


def get_coords_from_google_url(url):
    try:
        if url.find("ll=") != -1:
            latitude = url.split("ll=")[1].split(",")[0]
            longitude = url.split("ll=")[1].split(",")[1].split("&")[0]
        else:
            latitude = url.split("@")[1].split(",")[0]
            longitude = url.split("@")[1].split(",")[1]
    except IndexError:
        latitude, longitude = "<MISSING>", "<MISSING>"

    return latitude, longitude


def fetch_data():
    out = []
    locator_domain = "https://www.bettermedcare.com/"
    api_url = "https://www.bettermedcare.com/locations"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0"
    }

    session = SgRequests()
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    divs = tree.xpath("//div[contains(@class,'location ')]")

    for d in divs:
        location_name = "".join(
            d.xpath(".//h4[@class='location__title']/a/text()")
        ).strip()
        page_url = "".join(d.xpath(".//h4[@class='location__title']/a/@href"))
        line = "".join(
            d.xpath(".//div[@class='location__body']/p[last()]/text()")
        ).strip()

        street_address, city, state, postal = get_address(line)
        country_code = "US"
        store_number = "<MISSING>"
        phone = (
            "".join(
                d.xpath(
                    ".//div[@class='location__links']/a[contains(@href, 'tel')]/text()"
                )
            ).strip()
            or "<MISSING>"
        )

        text = "".join(
            d.xpath(".//div[@class='location__links']/a[@class='location__link']/@href")
        )
        latitude, longitude = get_coords_from_google_url(text)
        location_type = "<MISSING>"
        hours_of_operation = (
            "".join(
                d.xpath(
                    ".//div[@class='location__body']/p[contains(text(), 'Hours')]/text()"
                )
            )
            .replace("Hours", "Everyday")
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
