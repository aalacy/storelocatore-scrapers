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
        "".join(re.findall(r'"latitude":(\d{2}.\d+)', text)).strip() or "<MISSING>"
    )
    longitude = (
        "".join(re.findall(r'"longitude":(-?\d{2,3}.\d+)', text)).strip() or "<MISSING>"
    )
    return latitude, longitude


def get_exception_locations():
    rows = []
    locator_domain = "https://chickiesandpetes.com/"
    page_url = "https://chickiesandpetes.com/location/shore-locations/"

    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    divs = tree.xpath("//div[@class='col-md-6']/p[not(@style) and not(./iframe)]")

    for d in divs:
        location_name = "".join(d.xpath("./preceding-sibling::h4/text()")).strip()
        line = "".join(d.xpath("./text()")).strip()
        adr = line.split("–")[0].strip()

        street_address, city, state, postal = get_address(adr)
        country_code = "US"
        store_number = "<MISSING>"
        phone = line.split("–")[1].strip()
        latitude, longitude = "<MISSING>", "<MISSING>"
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
        rows.append(row)

    return rows


def get_urls():
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    r = session.get("https://chickiesandpetes.com/location/", headers=headers)
    tree = html.fromstring(r.text)

    return tree.xpath("//div[@class='info']/h2/a/@href")


def get_data(page_url):
    locator_domain = "https://chickiesandpetes.com/"

    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)

    location_name = "".join(tree.xpath("//title/text()")).split("|")[0].strip()
    line = tree.xpath("//div[@class='wpsl-location-address']//text()")
    line = list(filter(None, [l.strip() for l in line]))
    if not line:
        return

    street_address = ", ".join(line[:-1])
    line = line[-1]
    city = line.split(",")[0].strip()
    line = line.split(",")[1].strip()
    state = line.split()[0]
    postal = line.split()[1]
    country_code = "US"
    store_number = "<MISSING>"
    phone = (
        "".join(tree.xpath("//div[@class='wpsl-location-phone']//text()"))
        .replace("Phone:", "")
        .strip()
        or "<MISSING>"
    )
    text = "".join(tree.xpath("//script[contains(text(), 'latitude')]/text()"))
    latitude, longitude = get_coords_from_text(text)
    location_type = "<MISSING>"

    hours = " ".join(
        "".join(tree.xpath("//div[@class='wpsl-location-additionalinfo']//text()"))
        .replace("Hours:", "")
        .split()
    )
    if "closed" in hours.lower():
        hours = "Temporarily Closed"
    if "Out" in hours:
        hours = hours.split("Out")[0].strip()
    if "Last" in hours:
        hours = hours.split("Last")[0].strip()

    hours_of_operation = hours or "<MISSING>"

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

    rows = get_exception_locations()
    for row in rows:
        out.append(row)

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
