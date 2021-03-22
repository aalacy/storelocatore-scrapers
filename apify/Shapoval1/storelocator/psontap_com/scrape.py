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

    r = session.get("https://www.psontap.com/")
    tree = html.fromstring(r.text)
    return tree.xpath("//div[@class='loc_dwn ']/ul/li/a/@href")


def get_data(url):
    locator_domain = "https://www.psontap.com/"
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
    r = session.get(page_url)

    tree = html.fromstring(r.text)
    ad = (
        " ".join(tree.xpath('//a[@class="loc_add_link"]/text()'))
        .replace("\r\n", "")
        .replace("  ", "")
        .strip()
    )
    a = usaddress.tag(ad, tag_mapping=tag)[0]
    street_address = f"{a.get('address1')} {a.get('address2')}".replace(
        "None", ""
    ).strip()
    city = a.get("city")
    state = a.get("state")
    postal = a.get("postal")
    country_code = "US"
    store_number = "<MISSING>"
    loc_name = "".join(
        tree.xpath('//h1[@class="loc_name"]/text() | //h2[@class="loc_name"]/text()')
    )
    slug = (
        "".join(tree.xpath('//div[@class="loc_city_hdr"]/text()'))
        .replace("\r\n", "")
        .replace("  ", "")
        .strip()
    )
    location_name = loc_name + " | " + slug
    phone = (
        "".join(
            tree.xpath('//div[@class="loc_phone"]/a[contains(@href, "tel")]/text()')
        )
        .replace("\r\n", "")
        .replace("  ", "")
        .strip()
    )
    text = "".join(tree.xpath('//a[@class="cta virtual_tour"]/@href'))
    try:
        if text.find("ll=") != -1:
            latitude = text.split("ll=")[1].split(",")[0]
            longitude = text.split("ll=")[1].split(",")[1].split("&")[0]
        else:
            latitude = text.split("@")[1].split(",")[0]
            longitude = text.split("@")[1].split(",")[1]
    except IndexError:
        latitude, longitude = "<MISSING>", "<MISSING>"
    location_type = "<MISSING>"
    hours_of_operation = tree.xpath(
        '//p[./strong[contains(text(), "Hours")]]/following-sibling::p/text()'
    )
    hours_of_operation = list(filter(None, [a.strip() for a in hours_of_operation]))
    hours_of_operation = " ".join(hours_of_operation)
    if hours_of_operation.find("11:00am – 3:00pm Sat/Sun") != -1:
        hours_of_operation = hours_of_operation.split("11:00am – 3:00pm Sat/Sun")[
            0
        ].strip()
    if hours_of_operation.find("Served") != -1:
        hours_of_operation = hours_of_operation.split("Served")[0].strip()
    temp_closed = "".join(tree.xpath('//div[@class="col-xs-12 col-sm-6"]/p/text()'))
    if temp_closed == "Temporarily closed.":
        hours_of_operation = "Temporarily closed"
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
