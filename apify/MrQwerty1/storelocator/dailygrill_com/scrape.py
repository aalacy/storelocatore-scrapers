import csv
import usaddress

from concurrent import futures
from lxml import html
from sgrequests import SgRequests
from urllib.parse import unquote


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
    street_address = f"{a.get('address1') or ''} {a.get('address2') or ''}".strip()
    if street_address == "None":
        street_address = "<MISSING>"
    city = a.get("city") or "<MISSING>"
    if "," in city:
        street_address += f' {city.split(",")[0].strip()}'
        city = city.split(",")[-1].strip()
    state = a.get("state") or "<MISSING>"
    postal = a.get("postal") or "<MISSING>"

    return street_address, city, state, postal


def get_params():
    params = []
    session = SgRequests()
    r = session.get("https://www.dailygrill.com/locations/")
    tree = html.fromstring(r.text)
    divs = tree.xpath(
        "//div[contains(@class, 'loc_block state_') and not(./div[contains(text(), 'Permanently')])]"
    )
    for d in divs:
        url = "".join(d.xpath("./a/@href"))
        phone = "".join(d.xpath(".//div[@class='loc_phone']/a/text()")) or "<MISSING>"
        params.append((url, phone))

    return params


def get_data(params):
    page_url = params[0]
    phone = params[1]
    locator_domain = "https://www.dailygrill.com/"

    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    location_name = "".join(
        tree.xpath(
            "//div[@class='loc_details light_marble']/*[@class='decorative']/text()"
        )
    ).strip()
    line = "".join(tree.xpath("//div[@class='store_address']//text()")).strip()
    street_address, city, state, postal = get_address(line)
    country_code = "US"
    store_number = "<MISSING>"
    text = "".join(tree.xpath("//a[@class='link_item cta slide-effect']/@href"))
    latitude, longitude = get_coords_from_google_url(unquote(text))
    location_type = "<MISSING>"

    _tmp = []
    days = tree.xpath("//div[@class='hours_block']/span/text()")
    times = tree.xpath("//div[@class='hours_block']/text()")
    times = list(filter(None, [t.strip() for t in times]))

    for d, t in zip(days, times):
        _tmp.append(f"{d.strip()} {t.strip()}")

    hours_of_operation = ";".join(_tmp) or "<MISSING>"
    isclosed = tree.xpath(
        "//div[@class='special_message' and .//*[contains(text(), 'temporarily')]]"
    )
    if isclosed:
        hours_of_operation = "Temporarily Closed"

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
    params = get_params()

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_data, param): param for param in params}
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
