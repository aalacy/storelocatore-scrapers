import csv
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
    urls = []
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:84.0) Gecko/20100101 Firefox/84.0"
    }

    r = session.get("https://www.nafnafgrill.com/locations/", headers=headers)
    tree = html.fromstring(r.text)
    li = tree.xpath("//li[@class='location-info-wrapper']")

    for l in li:
        url = "".join(l.xpath(".//h5/a/@href"))
        coord = (
            "".join(l.xpath(".//div[@data-markerlat]/@data-markerlat")),
            "".join(l.xpath(".//div[@data-markerlon]/@data-markerlon")),
        )
        urls.append((url, coord))

    return urls


def get_data(url):
    locator_domain = "https://www.nafnafgrill.com/"
    page_url = url[0]
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:84.0) Gecko/20100101 Firefox/84.0"
    }

    session = SgRequests()
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)

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

    location_name = "".join(
        tree.xpath("//span[@class='fl-heading-text']/text()")
    ).strip()
    line = tree.xpath("//div[@class='fl-rich-text']/p/text()")[1]
    a = usaddress.tag(line, tag_mapping=tag)[0]
    street_address = f"{a.get('address1')} {a.get('address2') or ''}".strip()
    if street_address == "None":
        street_address = "<MISSING>"
    city = a.get("city") or "<INACCESSIBLE>"
    state = a.get("state") or "<INACCESSIBLE>"
    postal = a.get("postal") or "<INACCESSIBLE>"
    country_code = "US"
    if street_address.find(", Mt.") != -1:
        street_address = street_address.replace(", Mt.", "")
        city = f"Mt. {city}"

    store_number = "<MISSING>"
    phone = (
        "".join(
            tree.xpath(
                "//p[@class='uabb-infobox-title' and not(contains(text(), 'Back'))]/text()"
            )
        ).strip()
        or "<MISSING>"
    )
    latitude, longitude = url[1]
    location_type = "<MISSING>"

    _tmp = []
    divs = tree.xpath("//div[contains(@class, 'uabb-business-hours-wrap')]")

    for d in divs:
        line = " ".join("".join(d.xpath(".//text()")).split())
        _tmp.append(line)

    hours_of_operation = ";".join(_tmp) or "<MISSING>"
    if hours_of_operation.lower().count("closed") == 7:
        hours_of_operation = "Closed"

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
