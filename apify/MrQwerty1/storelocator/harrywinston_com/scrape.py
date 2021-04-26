import csv
import re
import usaddress

from concurrent import futures
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


def get_coords_from_text(text):
    latitude = (
        "".join(re.findall(r'"Latitude":"(\d{2}.\d+)"', text)).strip() or "<MISSING>"
    )
    longitude = (
        "".join(re.findall(r'"Longitude":"(-?\d{2,3}.\d+)"', text)).strip()
        or "<MISSING>"
    )
    return latitude, longitude


def get_urls():
    session = SgRequests()
    r = session.get("https://www.harrywinston.com/sitemap.xml")
    tree = html.fromstring(r.content)

    return tree.xpath("//loc[contains(text(),'/en/locations/north-america/')]/text()")


def get_data(page_url):
    locator_domain = "https://www.harrywinston.com/"

    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    location_name = "".join(tree.xpath("//h1/text()")).strip()
    line = " ".join(
        "".join(tree.xpath("//span[@class='location-detail__address']/text()")).split()
    )
    if not line:
        return
    if "Center" in line:
        line = line.split("Center")[-1].strip()
    if "Plaza" in line:
        line = line.split("Plaza")[-1].strip()

    street_address, city, state, postal = get_address(line)
    country_code = "US"
    store_number = "<MISSING>"
    try:
        phone = tree.xpath("//a[@class='location-detail__phone']/text()")[0].strip()
    except IndexError:
        phone = "<MISSING>"
    text = "".join(tree.xpath("//div[@data-properties]/@data-properties")).replace(
        "&quot;", '"'
    )
    latitude, longitude = get_coords_from_text(text)
    location_type = "<MISSING>"

    _tmp = []
    days = tree.xpath("//p[@class='location-detail__hours-heading']/text()")
    times = tree.xpath("//p[@class='location-detail__hours-description']/text()")

    for d, t in zip(days, times):
        _tmp.append(f"{d.strip()}: {t.strip()}")

    hours_of_operation = ";".join(_tmp) or "<MISSING>"

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

    return row


def fetch_data():
    out = []
    urls = get_urls()

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_data, url): url for url in urls}
        for future in futures.as_completed(future_to_url):
            row = future.result()
            if row:
                out.append(row)

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
