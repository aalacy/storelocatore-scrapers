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
    r = session.get("http://www.ifreshmarket.com/en/stores/")
    tree = html.fromstring(r.text)

    return tree.xpath('//div[@class="portfolio-item-hover"]/a/@href')


def get_data(url):
    locator_domain = "http://www.ifreshmarket.com"
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

    ad = (
        " ".join(
            tree.xpath(
                '//h6[./strong[contains(text(), "Address")]]/following-sibling::p[1]/text()'
            )
        )
        .replace("NY11354", "NY 11354")
        .replace("NY11229", "NY 11229")
    )
    a = usaddress.tag(ad, tag_mapping=tag)[0]

    street_address = f"{a.get('address1')} {a.get('address2')}".replace(
        "None", ""
    ).strip()
    city = "".join(a.get("city")).replace("，", "") or "<MISSING>"
    state = a.get("state") or "<MISSING>"
    postal = a.get("postal") or "<MISSING>"
    country_code = "US"
    store_number = "<MISSING>"
    location_name = "".join(tree.xpath("//h1/text()")).replace("\n", "").strip()
    phone = (
        "".join(
            tree.xpath(
                '//h6[./strong[contains(text(), "Tel")]]/following-sibling::p[1]/text()'
            )
        )
        or "<MISSING>"
    )

    longitude = "<MISSING>"
    latitude = "<MISSING>"
    location_type = "<MISSING>"
    hours_of_operation = (
        "".join(
            tree.xpath(
                '//h6[./strong[contains(text(), "Business Hours")]]/following-sibling::p[2]//text()'
            )
        )
        .replace("\n", "")
        .strip()
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
