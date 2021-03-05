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


def clean_hoo(text):
    text = (
        text.lower()
        .replace("pm ", "pm;")
        .replace("closed ", "closed;")
        .replace("other hours by reservation", "")
        .replace("temporary hours (covid)", "")
        .replace("tbd", "<MISSING>")
        .replace("monday-saturday by appointment", "<MISSING>")
        .strip()
    )
    if text.find("(") != -1:
        text = text.split("(")[0] + text.split(")")[1].strip()
    if text.find("*") != -1:
        text = text.split("*")[-1].strip()
    if text.find("extended") != -1:
        text = text.split("extended")[0].strip()

    return text


def get_urls():
    session = SgRequests()
    r = session.get("https://www.stretchzone.com/locations/")
    tree = html.fromstring(r.text)

    return tree.xpath("//h2/a/@href")


def get_data(page_url):
    locator_domain = "https://www.stretchzone.com/"
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
    if location_name.lower().find("test ") != -1:
        return
    line = tree.xpath(
        "//a[contains(@href, 'http://maps.google.com/') or contains(@href, 'https://www.google.com/maps') or @class='address']/text()"
    )[0].strip()

    a = usaddress.tag(line, tag_mapping=tag)[0]
    street_address = f"{a.get('address1')} {a.get('address2') or ''}".strip()
    if street_address == "None":
        street_address = "<MISSING>"
    city = a.get("city") or "<MISSING>"
    state = a.get("state") or "<MISSING>"
    if state.find(",") != -1:
        state = state.split(",")[0]
    postal = a.get("postal") or "<MISSING>"

    country_code = "US"
    store_number = "<MISSING>"
    try:
        phone = tree.xpath("//a[@class='tel']/text()")[0].strip()
    except IndexError:
        phone = "<MISSING>"
    try:
        loc_line = tree.xpath(
            "//a[contains(@href, 'http://maps.google.com/') or contains(@href, 'https://www.google.com/maps') or @class='address']/@href"
        )[0]
        if loc_line.find("q=loc:") == -1:
            latitude, longitude = loc_line.split("/@")[1].split("z/")[0].split(",")[:2]
        else:
            latitude, longitude = loc_line.split("q=loc:")[1].split(",")
    except:
        latitude = "<MISSING>"
        longitude = "<MISSING>"
    location_type = "<MISSING>"

    hours = tree.xpath("//div[@class='text work-hours']/p/text()")
    hours = list(filter(None, [h.strip() for h in hours]))

    hours_of_operation = " ".join(hours) or "<MISSING>"
    if hours_of_operation != "<MISSING>":
        hours_of_operation = clean_hoo(hours_of_operation)

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
