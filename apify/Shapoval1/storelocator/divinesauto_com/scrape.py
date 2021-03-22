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
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0",
        "Accept": "*/*",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "X-Moz": "prefetch",
        "Referer": "https://divinesauto.com/convenience-stores/",
        "Connection": "keep-alive",
        "TE": "Trailers",
    }
    r = session.get("https://divinesauto.com/convenience-stores/", headers=headers)

    tree = html.fromstring(r.text)
    return tree.xpath('//li[@id="menu-item-295"]/ul/li/a/@href')


def get_data(url):
    locator_domain = "https://divinesauto.com"
    page_url = "".join(url)
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
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0",
        "Accept": "*/*",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "X-Moz": "prefetch",
        "Referer": "https://divinesauto.com/convenience-stores/",
        "Connection": "keep-alive",
        "TE": "Trailers",
    }
    r = session.get(page_url, headers=headers)

    tree = html.fromstring(r.text)

    line = " ".join(tree.xpath('//h3[@class="ttladrs"]/text()'))
    a = usaddress.tag(line, tag_mapping=tag)[0]
    street_address = f"{a.get('address1')} {a.get('address2')}".replace(
        "None", ""
    ).strip()
    city = a.get("city")
    state = a.get("state")
    postal = a.get("postal")
    country_code = "US"
    store_number = "<MISSING>"
    location_name = "".join(tree.xpath("//h1/text()"))
    phone = "".join(tree.xpath("//strong/a[contains(@href, 'tel')]/text()")) or "".join(
        tree.xpath(
            "//h3[./strong[contains(text(), 'Telephone')]]/following-sibling::p[1]//text()"
        )
    )
    ll = "".join(tree.xpath("//iframe/@data-lazy-src"))
    latitude = ll.split("!3d")[1].strip().split("!")[0].strip()
    longitude = ll.split("!2d")[1].strip().split("!")[0].strip()
    location_type = "<MISSING>"
    hours_of_operation = (
        " ".join(
            tree.xpath(
                "//h3[./strong[contains(text(), 'Station’s Hours')]]/following-sibling::p[1]//text() | //h3[./strong[contains(text(), 'Store Hours')]]/following-sibling::p[1]//text()"
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
