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
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0",
        "Accept": "*/*",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Content-Type": "application/json",
        "Origin": "https://theyard.com",
        "Connection": "keep-alive",
        "Referer": "https://theyard.com/philadelphia-coworking-office-space/",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
    }

    session = SgRequests()
    r = session.get("https://theyard.com/", headers=headers)
    tree = html.fromstring(r.text)

    return tree.xpath('//a[./span[@class="image-holder"]]/@href')


def get_data(url):
    locator_domain = "https://theyard.com"
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
        tree.xpath('//div[@class="back-link"]/following-sibling::address[1]/p/text()')
    )
    line = line.split(",")[:-1]
    line = "".join(line)
    a = usaddress.tag(line, tag_mapping=tag)[0]
    street_address = f"{a.get('address1')} {a.get('address2')}".replace(
        "None", ""
    ).strip()
    city = a.get("city")
    state = a.get("state")
    postal = a.get("postal") or "<MISSING>"
    country_code = " ".join(
        tree.xpath('//div[@class="back-link"]/following-sibling::address[1]/p/text()')
    ).split(",")[-1]
    page_url = url

    store_number = "<MISSING>"
    location_name = tree.xpath(
        '//div[@class="back-link"]/following-sibling::h1[1]/text()'
    )
    location_name = list(filter(None, [a.strip() for a in location_name]))
    location_name = " ".join(location_name).replace("\n", " ")
    phone = (
        "".join(
            tree.xpath('//div[@class="manager-block"]/p[contains(text(), "(")]/text()')
        ).strip()
        or "<MISSING>"
    )
    latitude = "".join(tree.xpath('//div[@id="map"]/@data-latitude')).strip()
    longitude = "".join(tree.xpath('//div[@id="map"]/@data-longitude')).strip()
    location_type = "<MISSING>"
    hours_of_operation = (
        " ".join(tree.xpath("//header/ul/li/text()")).replace("\n", "").strip()
    )
    if street_address.find("13th") != -1:
        hours_of_operation = hours_of_operation.split("Manhattan – 23 minutes")[
            1
        ].strip()

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
