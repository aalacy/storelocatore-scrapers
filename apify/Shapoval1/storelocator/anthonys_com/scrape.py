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
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Referer": "https://www.anthonys.com/",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
        "TE": "Trailers",
    }
    r = session.get("https://www.anthonys.com/sitemap.xml", headers=headers)
    tree = html.fromstring(r.content)
    return tree.xpath("//url/loc[contains(text(), 'restaurant')]/text()")


def get_data(url):
    locator_domain = "https://www.anthonys.com"
    page_url = url
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Referer": "https://www.anthonys.com/",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
        "TE": "Trailers",
    }
    r = session.get(page_url, headers=headers)
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
    tree = html.fromstring(r.text)
    ad = " ".join(
        tree.xpath('//div[@class="left-column-content column-content"]/h3[1]/text()')
    ).replace("\n", "")
    a = usaddress.tag(ad, tag_mapping=tag)[0]
    street_address = f"{a.get('address1')} {a.get('address2')}".replace(
        "None", ""
    ).strip()
    city = a.get("city")
    state = a.get("state")
    postal = a.get("postal")
    country_code = "US"
    page_url = "".join(url)
    if page_url.find("https://www.anthonys.com/restaurants/") != -1:
        return
    store_number = "<MISSING>"
    location_name = "".join(
        tree.xpath('//h2[@class="intro-content-title"]/text()')
    ).strip()
    phone = "".join(
        tree.xpath(
            '//h3[contains(text(), "Contact")]/following-sibling::p/a[contains(@href, "tel")]/text() | //h3[contains(text(), "Contact")]/following-sibling::p/text() | //h3[contains(text(), "Phone")]/following-sibling::p/a[contains(@href, "tel")]/text()'
        )
    ).strip()
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    location_type = "<MISSING>"
    hours_of_operation = (
        " ".join(
            tree.xpath(
                '//h3[1][contains(text(),"Hours")]/following-sibling::p[1]/text() | //h3[1][contains(text(),"Indoor Dining")]/following-sibling::p[1]/text()'
            )
        )
        .replace("\n", "")
        .strip()
    )
    if hours_of_operation.find("Coming soon") != -1:
        hours_of_operation = "Coming soon"
    if hours_of_operation.find("Closed for the season") != -1:
        hours_of_operation = "Temporarily closed"
    if hours_of_operation.find("Temporarily Closed") != -1:
        hours_of_operation = "Temporarily closed"
    if hours_of_operation.find("Anthony’s Cabana") != -1:
        hours_of_operation = "<MISSING>"
    if hours_of_operation.find("Not currently available.") != -1:
        hours_of_operation = "Closed"
    if street_address.find("1207") != -1:
        hours_of_operation = (
            " ".join(
                tree.xpath(
                    '//h3[contains(text(),"Hours:")]/following-sibling::div[1]//text()'
                )
            )
            .replace("\n", "")
            .strip()
        )
    if street_address.find("550") != -1:
        hours_of_operation = hours_of_operation.split("call")[1].strip()
    if location_name.find("Anthony’s Cabana") != -1:
        hours_of_operation = "Closed"
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
