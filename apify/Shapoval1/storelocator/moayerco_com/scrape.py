import csv
import usaddress
from concurrent import futures
from lxml import html
from sgrequests import SgRequests


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
    r = session.get("https://www.moayerco.com/missouri-ayerco-locations/")
    tree = html.fromstring(r.text)

    return tree.xpath("//a[contains(text(), 'View Store')]/@href")


def get_data(url):
    locator_domain = "https://www.moayerco.com"
    page_url = f"https://www.moayerco.com/{url}"
    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)
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
    location_name = " ".join(tree.xpath("//h2[@class='panel-title']/text()")).strip()
    line = tree.xpath("//strong[.='Hours:']/preceding-sibling::text()[position() < 4]")
    line = list(filter(None, [a.strip() for a in line]))
    line = " ".join(line)
    a = usaddress.tag(line, tag_mapping=tag)[0]
    street_address = (
        f"{a.get('address1')} {a.get('address2')}".replace("None", "").strip()
        or "<MISSING>"
    )
    city = "".join(a.get("city"))
    state = "".join(a.get("state"))
    postal = "".join(a.get("postal"))
    country_code = "US"
    store_number = " ".join(tree.xpath("//h2[@class='panel-title']/text()"))
    if store_number.find("#") != -1:
        store_number = "".join(store_number.split("#")[1])
    else:
        store_number = "<MISSING>"
    phone = (
        "".join(
            tree.xpath("//strong[2]/following-sibling::text()[position() = 1]")
        ).strip()
        or "<MISSING>"
    )
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    location_type = "<MISSING>"
    hours_of_operation = (
        "".join(tree.xpath("//strong[1]/following-sibling::text()[position() = 1]"))
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
