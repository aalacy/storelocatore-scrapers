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
    session = SgRequests()
    r = session.get("https://primary-health.net/Locations.aspx")
    tree = html.fromstring(r.text)

    return tree.xpath("//a[contains(@id, '_SiteLink_')]/@href")


def get_data(url):
    locator_domain = "https://primary-health.net/"
    page_url = f"{locator_domain}{url}"

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

    location_name = "".join(tree.xpath("//h1[@class='pull-left']/text()")).strip()
    line = "".join(
        tree.xpath("//span[@id='PageTitle_SiteList2_AddressLabel_0']/text()")
    ).strip()

    a = usaddress.tag(line, tag_mapping=tag)[0]
    street_address = f"{a.get('address1')} {a.get('address2') or ''}".strip()
    if street_address == "None":
        street_address = "<MISSING>"
    city = a.get("city") or "<INACCESSIBLE>"
    state = a.get("state") or "<INACCESSIBLE>"
    postal = a.get("postal") or "<INACCESSIBLE>"
    country_code = "US"

    store_number = page_url.split("=")[-1]
    phone = (
        "".join(
            tree.xpath("//span[@id='PageTitle_SiteList2_PhoneLabel_0']/text()")
        ).strip()
        or "<MISSING>"
    )

    text = "".join(tree.xpath("//meta[@name='keywords']/@content")).split()[:2]
    latitude, longitude = "<MISSING>", "<MISSING>"
    for t in text:
        if "long" in t:
            longitude = t.replace("long", "").replace(",", "").replace(";", "").strip()
        if "lat" in t:
            latitude = t.replace("lat", "").replace(",", "").replace(";", "").strip()
    location_type = "<MISSING>"

    _tmp = []
    hours = tree.xpath("//span[@id='Content_SiteList_HoursLabel_0']/text()")
    hours = list(filter(None, [h.strip() for h in hours]))
    for h in hours:
        if "Dental" in h or "*" in h or "For Hours" in h:
            break
        if "temporarily closed" in h:
            _tmp.append("Temporarily Closed")
            break
        _tmp.append(h)

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
