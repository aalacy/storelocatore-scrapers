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
    }
    cookies = {
        "0df70ee305b6cb200ce1c1e691debe0f": "f3c0a08d7b8484f3a53105083de4e2c8",
        "_ga": "GA1.2.1540435124.1616279320",
        "_gid": "GA1.2.1341765674.1616279320",
        "_fbp": "fb.1.1616279320891.257561148",
    }
    r = session.get(
        "https://clubchampiongolf.com/index.php?option=com_jmap&view=sitemap&format=xml",
        headers=headers,
        cookies=cookies,
    )
    tree = html.fromstring(r.content)
    return tree.xpath("//*[contains(text(), 'location/')]/text()")


def get_data(url):
    locator_domain = "https://clubchampiongolf.com"
    page_url = "".join(url)
    if page_url.find("mass") != -1:
        return
    session = SgRequests()
    cookies = {
        "0df70ee305b6cb200ce1c1e691debe0f": "f3c0a08d7b8484f3a53105083de4e2c8",
        "_ga": "GA1.2.1540435124.1616279320",
        "_gid": "GA1.2.1341765674.1616279320",
        "_fbp": "fb.1.1616279320891.257561148",
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0",
    }
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
    r = session.get(page_url, headers=headers, cookies=cookies)
    tree = html.fromstring(r.text)

    ad = tree.xpath("//tr//span//text()")
    ad = " ".join(ad[1:])
    if ad.find("(") != -1:
        ad = ad.split("(")[0].strip()
    a = usaddress.tag(ad, tag_mapping=tag)[0]
    street_address = f"{a.get('address1')} {a.get('address2')}".replace(
        "None", ""
    ).strip()
    city = a.get("city")
    state = a.get("state")
    postal = a.get("postal")
    country_code = "US"
    store_number = "<MISSING>"
    location_name = "".join(
        tree.xpath(
            '//div[@class="uk-panel cc-loc-h1 h1-mobile-dt uk-width-xlarge"]/h1/text()'
        )
    )
    phone = "".join(
        tree.xpath('//tbody//td[2]//a[contains(@href, "tel")]/text()')
    ).strip()
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    location_type = "<MISSING>"
    hours_of_operation = " ".join(
        tree.xpath("//div[./h3]/following-sibling::div[1]//text()")
    )
    if hours_of_operation.find("GET") != -1:
        hours_of_operation = hours_of_operation.split("GET")[0].strip()
    if hours_of_operation.find("Get") != -1:
        hours_of_operation = hours_of_operation.split("Get")[0].strip()

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
