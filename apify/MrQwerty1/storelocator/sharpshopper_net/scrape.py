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


def get_urls():
    session = SgRequests()
    r = session.get("http://sharpshopper.net/")
    tree = html.fromstring(r.text)

    return tree.xpath("//a[text()='Locations']/following-sibling::ul[1]//a/@href")


def get_data(url):
    locator_domain = "http://sharpshopper.net/"
    page_url = f"{locator_domain}{url}"

    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    location_name = "".join(tree.xpath("//title/text()")).strip()
    line = tree.xpath("//h1/text()")
    line = list(filter(None, [l.strip() for l in line]))
    line = ", ".join(line[1:])
    if "Centre," in line:
        line = line.split("Centre,")[1].strip()

    street_address, city, state, postal = get_address(line)
    country_code = "US"
    store_number = "<MISSING>"
    phone = (
        "".join(
            tree.xpath("//div[@class='contentright']/h3/following-sibling::p[1]/text()")
        ).strip()
        or "<MISSING>"
    )
    if "Phone" in phone:
        phone = phone.split("Phone")[1].replace("#", "").replace(":", "").strip()
    if "Fax" in phone:
        phone = phone.split("Fax")[0].strip()
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    location_type = location_name.split()[-1]

    hours = tree.xpath(
        "//h2[contains(text(), ' Hours')]/following-sibling::p[1]//text()"
    )
    hours = list(filter(None, [h.strip() for h in hours]))
    hours_of_operation = " ".join(hours) or "<MISSING>"
    if "The Corporate" in hours_of_operation:
        hours_of_operation = (
            hours_of_operation.split("The Corporate")[0].strip() + " Closed"
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

    return row


def fetch_data():
    out = []
    urls = get_urls()

    with futures.ThreadPoolExecutor(max_workers=11) as executor:
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
