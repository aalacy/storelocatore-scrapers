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
    r = session.get("https://www.rajbhog.com/locations/")
    tree = html.fromstring(r.text)
    return tree.xpath("//div/h4/a/@href")


def get_data(url):
    locator_domain = "https://www.rajbhog.com"
    page_url = url
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

    line = " ".join(
        tree.xpath(
            '//div[./strong[contains(text(), "Address")]]/text() | //div[./strong[contains(text(), "Addess")]]/text()'
        )
    ).strip()

    a = usaddress.tag(line, tag_mapping=tag)[0]
    street_address = f"{a.get('address1')} {a.get('address2')}".replace(
        "None", ""
    ).strip()
    city = a.get("city")
    if city.find("Fabrics") != -1:
        city = city.split("Fabrics")[1].strip()
    state = a.get("state")
    postal = a.get("postal") or "<MISSING>"
    if postal == "<MISSING>":
        postal = (
            "".join(tree.xpath("//iframe/@src")).split("%20")[6].split("%")[0].strip()
        )
    country_code = "US"
    store_number = "<MISSING>"
    location_name = "".join(tree.xpath("//title/text()"))
    phone = (
        "".join(tree.xpath('//a[./strong[contains(text(), "Phone")]]/text()')).strip()
        or "<MISSING>"
    )

    map_link = "".join(tree.xpath("//iframe/@src"))
    latitude = map_link.split("!3d")[1].strip().split("!")[0].strip()
    longitude = map_link.split("!2d")[1].strip().split("!")[0].strip()
    location_type = "<MISSING>"
    slug = "".join(
        tree.xpath('//a[./span[contains(text(), "Working Hours")]]/@href')
    ).strip()
    hours_url = f"{page_url}{slug}"
    hours_of_operation = (
        " ".join(
            tree.xpath(
                '//h2[contains(text(), "Working")]/following-sibling::div[1]//span/text()'
            )
        )
        .replace("\n", "")
        .strip()
        or "<MISSING>"
    )

    if hours_of_operation == "<MISSING>":
        session = SgRequests()
        r = session.get(hours_url)
        tree = html.fromstring(r.text)
        hours_of_operation = (
            " ".join(tree.xpath("//table//span/text()")).replace("\n", "").strip()
        )
    hours_of_operation = hours_of_operation.replace("Â", "").strip()
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
