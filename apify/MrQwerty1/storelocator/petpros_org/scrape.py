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

    for i in range(1, 5000):
        r = session.get(f"https://shop.petpros.net/stores/search/?page={i}")
        tree = html.fromstring(r.text)
        links = tree.xpath("//a[@class='pull-right']/@href")
        urls += links
        if len(links) < 10:
            break

    return urls


def get_data(url):
    locator_domain = "https://petpros.org/"
    page_url = f"https://shop.petpros.net{url}"

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

    location_name = "".join(tree.xpath("//h1[@class='banner-heading']/text()")).strip()
    line = "".join(
        tree.xpath("//a[contains(@href, 'map')]/div[@class='stre-icns-dtl']/text()")
    ).strip()
    a = usaddress.tag(line, tag_mapping=tag)[0]
    street_address = f"{a.get('address1')} {a.get('address2') or ''}".strip()
    if street_address == "None":
        street_address = "<MISSING>"
    city = a.get("city") or "<INACCESSIBLE>"
    state = a.get("state") or "<INACCESSIBLE>"
    postal = a.get("postal").strip() or "<INACCESSIBLE>"
    country_code = "US"
    store_number = "<MISSING>"
    phone = (
        "".join(
            tree.xpath(
                "//a[contains(@href, 'tel')]/div[@class='stre-icns-dtl arial-font']/text()"
            )
        ).strip()
        or "<MISSING>"
    )

    text = "".join(
        tree.xpath("//script[contains(text(), 'var latitude')]/text()")
    ).strip()
    latitude = text.split('var latitude = "')[1].split('";')[0]
    longitude = text.split('var longitude = "')[1].split('";')[0]
    location_type = "<MISSING>"

    _tmp = []
    divs = tree.xpath("//div[@class='row stre-opn-tmngs']")

    for d in divs:
        day = "".join(d.xpath("./div[1]/text()")).strip()
        time = "".join(d.xpath("./div[3]/text()")).strip()
        _tmp.append(f"{day}: {time}")

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
