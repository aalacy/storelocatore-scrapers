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
    locator_domain = "https://www.thedump.com"
    api_url = "https://www.thedump.com/locations"

    session = SgRequests()
    r = session.get(api_url)
    tree = html.fromstring(r.text)
    divs = tree.xpath("//div[@class='col-md-4 thedump-location-block']")
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

    for d in divs:
        line = "".join(
            d.xpath(".//div[@class='thedump-location-address']/text()")
        ).strip()
        a = usaddress.tag(line, tag_mapping=tag)[0]
        street_address = f"{a.get('address1')} {a.get('address2') or ''}".strip()
        if street_address == "None":
            street_address = "<MISSING>"
        city = a.get("city") or "<INACCESSIBLE>"
        state = a.get("state") or "<INACCESSIBLE>"
        postal = a.get("postal") or "<INACCESSIBLE>"
        country_code = "US"

        store_number = "<MISSING>"
        slug = "".join(
            d.xpath(
                ".//div[@class='thedump-location-photo scale-image-effect']/a/@href"
            )
        )
        if slug != "#":
            page_url = f"{locator_domain}{slug}"
        else:
            page_url = api_url

        location_name = "".join(
            d.xpath(".//div[@class='thedump-location-title']/h3/a/text()")
        ).strip()
        phone = (
            "".join(d.xpath(".//div[@class='thedump-location-phone']/a/text()"))
            or "<MISSING>"
        )

        text = "".join(
            d.xpath(".//a[@class='button small-button lightbox mfp-iframe']/@href")
        )
        latitude, longitude = get_coords_from_google_url(text)
        location_type = "<MISSING>"

        hours = d.xpath(".//span[@style='color:#000']//text()")
        hours = list(filter(None, [h.strip() for h in hours]))

        hours_of_operation = (
            "".join(hours)
            .replace("6M", "6M;")
            .replace("PM", "PM;")
            .replace(";View on Map", "")
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
