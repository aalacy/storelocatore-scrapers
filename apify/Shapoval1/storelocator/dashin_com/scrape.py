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
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Referer": "https://locations.dashin.com/",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }
    r = session.get("https://locations.dashin.com/", headers=headers)
    tree = html.fromstring(r.text)
    return tree.xpath("//h5/following-sibling::ul/li/a/@href")


def get_data(url):
    locator_domain = "https://dashin.com/"
    page_url = "https://locations.dashin.com" + url
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Referer": "https://locations.dashin.com/",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }
    if (
        page_url
        == "https://locations.dashin.com/l/md/dash-in-3075-solomon's-island-road-21401/60907f95e4b082a532e142c8"
    ):
        return
    if (
        page_url
        == "https://locations.dashin.com/l/md/dash-in-3620-mattawoman/beantown-road-20601/60907f95e4b06381bd5dcddb"
    ):
        return
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
    ad = tree.xpath('//a[@title="Get Directions"]/text()')
    ad = list(filter(None, [a.strip() for a in ad]))
    ad = " ".join(ad)
    a = usaddress.tag(ad, tag_mapping=tag)[0]
    street_address = (
        f"{a.get('address1')} {a.get('address2')}".replace("None", "").strip()
        or "<MISSING>"
    )
    city = a.get("city") or "<MISSING>"
    state = a.get("state") or "<MISSING>"
    postal = a.get("postal") or "<MISSING>"
    if street_address.find("6985 Indian Head Highway Bryans Road") != -1:
        city = " ".join(street_address.split()[-2:])
        street_address = " ".join(street_address.split()[:-2])
    country_code = "US"
    store_number = "<MISSING>"
    location_name = (
        "".join(tree.xpath("//h1/text()")).strip().capitalize() or "<MISSING>"
    )
    phone = (
        "".join(tree.xpath('//h6[text()="Phone"]/following-sibling::p[1]/a/text()'))
        or "<MISSING>"
    )
    try:
        latitude = (
            "".join(
                tree.xpath('//script[contains(text(), "const coordinates")]/text()')
            )
            .split("lat:")[1]
            .split(",")[0]
            .strip()
        )
        longitude = (
            "".join(
                tree.xpath('//script[contains(text(), "const coordinates")]/text()')
            )
            .split("lng:")[1]
            .split("}")[0]
            .strip()
        )
    except:
        latitude, longitude = "<MISSING>", "<MISSING>"
    location_type = "<MISSING>"
    hours_of_operation = (
        "".join(tree.xpath('//h6[text()="Hours"]/following-sibling::p//text()'))
        .replace("\n", "")
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
