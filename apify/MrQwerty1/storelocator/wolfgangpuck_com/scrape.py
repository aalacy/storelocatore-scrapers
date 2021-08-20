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


def get_urls():
    session = SgRequests()
    r = session.get("https://wolfgangpuck.com/")
    tree = html.fromstring(r.text)

    return tree.xpath("//a[contains(@href, 'https://wolfgangpuck.com/dining/')]/@href")


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


def get_coords_from_text(text):
    latitude = (
        "".join(re.findall(r'"latitude":(\s+?\d{2}.\d+)', text)).strip() or "<MISSING>"
    )
    longitude = (
        "".join(re.findall(r'"longitude":(\s+?-?\d{2,3}.\d+)', text)).strip()
        or "<MISSING>"
    )
    return latitude, longitude


def get_data(page_url):
    locator_domain = "https://wolfgangpuck.com/"
    states = [
        "AL",
        "AK",
        "AZ",
        "AR",
        "CA",
        "CO",
        "CT",
        "DC",
        "DE",
        "FL",
        "GA",
        "HI",
        "ID",
        "IL",
        "IN",
        "IA",
        "KS",
        "KY",
        "LA",
        "ME",
        "MD",
        "MA",
        "MI",
        "MN",
        "MS",
        "MO",
        "MT",
        "NE",
        "NV",
        "NH",
        "NJ",
        "NM",
        "NY",
        "NC",
        "ND",
        "OH",
        "OK",
        "OR",
        "PA",
        "RI",
        "SC",
        "SD",
        "TN",
        "TX",
        "UT",
        "VT",
        "VA",
        "WA",
        "WV",
        "WI",
        "WY",
        "London",
    ]

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
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    location_name = "".join(tree.xpath("//h1/text()")).strip()
    line = " ".join(
        "".join(tree.xpath("//span[@class='schema-address']/text()")).split()
    )
    if not line:
        line = " ".join(
            "".join(tree.xpath("//div[@class='col-sm-6']/p[1][./a]/text()")).split()
        )

    for s in states:
        if s in line:
            break
    else:
        return

    if "London" not in line:
        a = usaddress.tag(line, tag_mapping=tag)[0]
        street_address = f"{a.get('address1')} {a.get('address2') or ''}".strip()
        if street_address == "None":
            street_address = "<MISSING>"
        city = a.get("city") or "<MISSING>"
        state = a.get("state") or "<MISSING>"
        postal = a.get("postal") or "<MISSING>"
        country_code = "US"
    else:
        street_address = line.split(",")[0]
        city = line.split(",")[-1].strip()
        state = line.split(",")[-1].strip()
        postal = "<MISSING>"
        country_code = "GB"

    store_number = "<MISSING>"
    try:
        phone = (
            tree.xpath("//a[contains(@href, 'tel:')]/@href")[0]
            .replace("tel:", "")
            .strip()
        )
    except IndexError:
        phone = "<MISSING>"

    text = "".join(tree.xpath("//a[@class='map']/@href")).strip()
    if text:
        latitude, longitude = get_coords_from_google_url(text)
    else:
        text = "".join(tree.xpath("//script[@type='application/ld+json']/text()"))
        latitude, longitude = get_coords_from_text(text)
    location_type = "<MISSING>"
    hours = tree.xpath(
        "//div[@class='location-hours']/div/text()|//div[@class='col-sm-6']/p[./strong[text()='Hours']]/text()"
    )
    hours = (
        "".join(hours)
        .replace("HOURS", "")
        .replace("Hours of Operation", "")
        .replace("Hours of operation", "")
        .strip()
        .split("\r\n")
    )
    hours = list(filter(None, [h.strip() for h in hours]))

    hours_of_operation = ";".join(hours).replace(":;", "") or "<MISSING>"

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
