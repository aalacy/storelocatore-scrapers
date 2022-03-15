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
    r = session.get("https://www.thelinehotel.com/")
    tree = html.fromstring(r.text)

    return tree.xpath("//div[@class='holder']/a/@href")


def get_data(url):
    locator_domain = "https://www.thelinehotel.com"
    page_url = f"{locator_domain}{url}"
    if page_url.find("sf") != -1:
        return
    session = SgRequests()
    r = session.get(page_url)

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

    hours_of_operation = "<MISSING>"

    country_code = "<MISSING>"
    aa = tree.xpath('//address[@class="address-global"]/a//text()') or tree.xpath(
        '//address[@class="address-global"]//text()'
    )
    aa = list(filter(None, [a.strip() for a in aa]))
    aa = " ".join(aa) or "<MISSING>"
    if aa.find("111") != -1:
        aa = aa.split("TEL")[0].strip()
    if aa.find("3515") != -1:
        aa = aa.split("213")[0].strip()
    if aa.find("1770") != -1:
        aa = aa.split("0525")[1].strip()
    a = usaddress.tag(aa, tag_mapping=tag)[0]
    street_address = (
        f"{a.get('address1')} {a.get('address2')}".replace("None", "").strip()
        or "<MISSING>"
    )
    postal = a.get("postal") or "<MISSING>"
    city = a.get("city") or "<MISSING>"
    state = a.get("state") or "<MISSING>"
    store_number = "<MISSING>"
    location_name = "".join(tree.xpath("//h1/text()")) or "".join(
        tree.xpath('//div[@class="inner"]/h2/text()')
    )
    phone = (
        " ".join(
            tree.xpath(
                '//section/following-sibling::address/a[contains(@href, "tel")]/text()'
            )
        )
        or "".join(tree.xpath('//p[contains(text(), "TEL")]/text()'))
        .replace("TEL:", "")
        .strip()
        or "".join(
            tree.xpath(
                '//section/following-sibling::address/p/a[contains(@href, "tel")]/text()'
            )
        ).replace("\n", "")
        or "<MISSING>"
    )
    ll = "".join(tree.xpath("//section/following-sibling::address/p/a[1]/@href"))
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    if page_url.find("austin") != -1:
        latitude = ll.split("/@")[1].split(",")[0]
        longitude = ll.split("/@")[1].split(",")[1]
    location_type = "<MISSING>"

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
