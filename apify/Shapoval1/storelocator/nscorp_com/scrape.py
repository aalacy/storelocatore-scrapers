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
    r = session.get(
        "http://www.nscorp.com/content/nscorp/en/shipping-options/intermodal/terminals-and-schedules.html",
        headers=headers,
    )
    tree = html.fromstring(r.text)
    return tree.xpath('//article[@class="toc"]//a/@href')


def get_data(url):
    locator_domain = "http://www.nscorp.com"
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
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0",
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)

    location_name = (
        "".join(tree.xpath('//div[@class="text parbase section"]/h4//text()'))
        .replace("\n", "")
        .replace("*", "")
        .strip()
    )

    ad = (
        " ".join(tree.xpath('//div[@class="mainpar parsys"]/div[2]//*/text()'))
        .replace("\n", "")
        .strip()
    )
    if ad.find("51 Foot") != -1:
        ad = ad.split("Hours")[0].strip()
    a = usaddress.tag(ad, tag_mapping=tag)[0]
    street_address = f"{a.get('address1')} {a.get('address2')} {a.get('recipient')} {a.get('SecondStreetName')}".replace(
        "None", ""
    ).strip()
    city = a.get("city") or "<MISSING>"
    state = a.get("state") or "<MISSING>"
    postal = a.get("postal") or "<MISSING>"
    country_code = "US"
    store_number = "<MISSING>"
    phone = (
        "".join(tree.xpath('//li[@class="phone"]//text()')).replace("\n", "").strip()
    )
    location_type = "<MISSING>"
    hours_of_operation = (
        " ".join(
            tree.xpath(
                '//h5[contains(text(),"Hours")]/following-sibling::p[1]/text() | //h5[text()="Hours of Operation"]/following-sibling::p[1]/text()'
            )
        )
        .replace("\n", "")
        .strip()
        or "<MISSING>"
    )
    if hours_of_operation.find("Inbound") != -1:
        hours_of_operation = hours_of_operation.split("Inbound")[0].strip()
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    if location_name == "Chicago, IL - Landers":
        street_address = (
            "".join(
                tree.xpath('//h5[text()="Address"]/following-sibling::p[1]/text()[2]')
            )
            .replace("\n", "")
            .strip()
        )
        ad = (
            "".join(
                tree.xpath('//h5[text()="Address"]/following-sibling::p[1]/text()[3]')
            )
            .replace("\n", "")
            .strip()
        )
        city = ad.split(",")[0].strip()
        state = ad.split(",")[1].split()[0].strip()
        postal = ad.split(",")[1].split()[1].strip()
    if street_address.find("Rt. 522") != -1:
        street_address = street_address + " " + city.split()[0]
        city = " ".join(city.split()[1:]).strip()

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
