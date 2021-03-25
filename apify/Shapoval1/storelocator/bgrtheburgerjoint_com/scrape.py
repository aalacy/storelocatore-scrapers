import csv
import usaddress
from lxml import html
from sgrequests import SgRequests
from concurrent import futures


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
    r = session.get("https://bgrtheburgerjoint.com/locations-menus/")
    tree = html.fromstring(r.text)
    return tree.xpath("//a[@class='et_pb_button et_pb_bg_layout_dark']/@href")


def get_data(url):
    locator_domain = "https://bgrtheburgerjoint.com"
    page_url = f"{locator_domain}{url}"
    session = SgRequests()
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
    r = session.get(page_url)
    tree = html.fromstring(r.text)
    line = (
        " ".join(
            tree.xpath(
                "//div[1][@class='x-text']/p/span/text() | //div[1][@class='x-text']/p/text()"
            )
        )
        .replace("\n", "")
        .strip()
    )
    if page_url.find("kuwait") != -1:
        return

    a = usaddress.tag(line, tag_mapping=tag)[0]
    street_address = (
        f"{a.get('address1')} {a.get('address2')} {a.get('recipient')}".replace(
            "None", ""
        ).strip()
    )
    city = a.get("city")
    state = a.get("state")
    postal = a.get("postal")
    country_code = "US"
    store_number = "<MISSING>"
    location_name = " ".join(
        tree.xpath("//div[@class='et_pb_text_inner']/h2//text()")
    ).split(",")[0]
    if page_url.find("bwi-airport") != -1:
        location_name = location_name.split("CREATE")[0].strip()
    if page_url.find("monroe-st") != -1:
        location_name = location_name.split("FEATURED")[0].strip()
    phone = (
        "".join(tree.xpath("//a[contains(@href, 'tel')]/text()"))
        .replace("Phone:", "")
        .strip()
    )
    latlon = "".join(tree.xpath("//div[contains(@id, 'wp_mapbox')]/@data-center"))
    latitude = latlon.split(",")[1].strip()
    longitude = latlon.split(",")[0].strip()
    location_type = "<MISSING>"
    hours_of_operation = (
        " ".join(tree.xpath("//div[2][@class='x-text']/p[1]//text()"))
        .replace("\n", " ")
        .strip()
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
