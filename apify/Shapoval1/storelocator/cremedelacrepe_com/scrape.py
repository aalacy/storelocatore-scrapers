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
    r = session.get("http://www.cremedelacrepe.com/")
    tree = html.fromstring(r.text)
    return tree.xpath('//a[@class="vcex-image-grid-entry-img"]/@href')


def get_data(url):
    locator_domain = "http://www.cremedelacrepe.com"
    page_url = f"{locator_domain}{url}"
    if page_url.find("catering") != -1:
        return
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

    location_name = "".join(tree.xpath("//h1/span/text()"))
    ad = tree.xpath('//div[@class="wpb_wrapper"]/div//p/text()')
    line = " ".join(ad[:2]).replace("\n", "").strip()
    if location_name.find("Rolling") != -1:
        line = " ".join(ad[:3]).replace("\n", "").strip()
    a = usaddress.tag(line, tag_mapping=tag)[0]
    street_address = f"{a.get('address1')} {a.get('address2')}".replace(
        "None", ""
    ).strip()
    city = a.get("city")
    state = a.get("state")
    postal = a.get("postal")

    country_code = "US"
    store_number = "<MISSING>"

    phone = "".join(ad[2]).replace("\n", "").split()[1].strip()
    if street_address.find("550") != -1:
        phone = "".join(ad[3]).replace("\n", "").split()[1].strip()
    latitude = (
        "".join(tree.xpath('//script[contains(text(), "var map")]/text()'))
        .split('center_lat":"')[1]
        .split('"')[0]
    )
    longitude = (
        "".join(tree.xpath('//script[contains(text(), "var map")]/text()'))
        .split('center_lng":"')[1]
        .split('"')[0]
    )
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
