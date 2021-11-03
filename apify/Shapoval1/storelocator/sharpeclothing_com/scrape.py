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
    r = session.get("https://sharpeclothing.com/our-stores/", headers=headers)
    tree = html.fromstring(r.text)
    return tree.xpath('//h3[@class="post-name h5"]/a/@href')


def get_data(url):
    locator_domain = "https://sharpeclothing.com/"
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
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0",
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    id = (
        "".join(tree.xpath('//body[contains(@class, "post-template-default")]/@class'))
        .split("postid-")[1]
        .split()[0]
        .strip()
    )
    id = "'" + id + "'"
    location_name = "".join(tree.xpath('//h1[@class="h1 post-name"]/text()'))
    ad = (
        " ".join(tree.xpath('//div[@class="blog-content wrapper-small"]/p[1]//text()'))
        .replace("\n", "")
        .strip()
    )
    a = usaddress.tag(ad, tag_mapping=tag)[0]
    street_address = f"{a.get('address1')} {a.get('address2')}".replace(
        "None", ""
    ).strip()
    city = a.get("city") or "<MISSING>"
    state = a.get("state") or "<MISSING>"
    postal = a.get("postal") or "<MISSING>"
    if ad.find("6818") != -1 or ad.find("201") != -1:
        street_address = " ".join(ad.split(",")[0].split()[:-1]).strip()
        city = ad.split(",")[0].split()[-1].strip()
        state = ad.split(",")[1].strip()
    if city == "<MISSING>":
        city = location_name.split(",")[0].strip()
    if state == "<MISSING>":
        state = location_name.split(",")[1].strip()
    country_code = "US"
    store_number = "<MISSING>"
    phone = (
        "".join(
            tree.xpath(
                '//div[@class="blog-content wrapper-small"]//a[contains(@href, "tel")]/text()'
            )
        )
        .replace("\n", "")
        .strip()
        or "<MISSING>"
    )
    if phone == "<MISSING>":
        phone = (
            "".join(
                tree.xpath('//div[@class="blog-content wrapper-small"]/p[2]/text()')
            )
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
    location_type = "<MISSING>"
    hours_of_operation = "<MISSING>"
    session = SgRequests()
    r = session.get("https://sharpeclothing.com/our-stores/", headers=headers)
    tree = html.fromstring(r.text)

    latitude = (
        "".join(tree.xpath('//script[contains(text(), "var infobox_xhr")]/text()'))
        .split(id)[1]
        .split(",")[1]
        .strip()
    )
    longitude = (
        "".join(tree.xpath('//script[contains(text(), "var infobox_xhr")]/text()'))
        .split(id)[1]
        .split(",")[2]
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
