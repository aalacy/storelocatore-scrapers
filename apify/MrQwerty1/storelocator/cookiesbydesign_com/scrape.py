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
    r = session.get("https://www.cookiesbydesign.com/locationsitemap.aspx")
    tree = html.fromstring(r.text)

    return tree.xpath("//ul[@id='ShoppeColumn']/li//a/@href")


def parse_corp(tree, page_url):
    locator_domain = "https://www.cookiesbydesign.com/"

    location_name = "".join(
        tree.xpath("//h2[@class='locationh2']/label/text()")
    ).strip()
    line = tree.xpath("//div[@class='col-md-4'][1]/text()")
    line = list(filter(None, [l.strip() for l in line]))
    street_address = ", ".join(line[:-1]) or "<MISSING>"
    line = line[-1]
    city = line.split(",")[0].strip()
    line = line.split(",")[1].strip()
    state = line.split()[0]
    postal = line.split()[1]
    country_code = "US"
    store_number = page_url.split("_")[-1].replace(".aspx", "")
    phone = "".join(tree.xpath("//a[@id='lnkPhone']/text()")).strip() or "<MISSING>"
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    location_type = "<MISSING>"

    _tmp = tree.xpath("//div[@class='col-md-4']/div/text()")
    _tmp = list(filter(None, [t.strip() for t in _tmp]))
    hours_of_operation = ";".join(_tmp) or "<MISSING>"
    if hours_of_operation.lower().find("temporarily closed") != -1:
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


def parse_frach(tree, page_url):
    locator_domain = "https://www.cookiesbydesign.com/"
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

    location_name = "".join(tree.xpath("//h1/text()")).strip()
    if not location_name:
        return
    line = "".join(tree.xpath("//input[@id='SAddressID']/@value"))
    a = usaddress.tag(line, tag_mapping=tag)[0]
    street_address = f"{a.get('address1')} {a.get('address2') or ''}".strip()
    if street_address == "None":
        street_address = "<MISSING>"
    city = a.get("city") or "<INACCESSIBLE>"
    state = a.get("state") or "<INACCESSIBLE>"
    postal = a.get("postal") or "<INACCESSIBLE>"
    country_code = "US"
    store_number = page_url.split("_")[-1].replace(".aspx", "")
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    location_type = "<MISSING>"

    _tmp = []
    lines = tree.xpath("//div[@class='bfm-location-address']//text()")
    phone = "<MISSING>"
    for l in lines:
        if l.lower().find("phone") != -1:
            phone = l.replace("Phone:", "").strip()
        if l.lower() == "hours":
            _tmp = lines[lines.index(l) + 1 :]
            break

    _tmp = list(filter(None, [t.strip() for t in _tmp]))
    hours_of_operation = ";".join(_tmp) or "<MISSING>"

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


def get_data(url):
    page_url = f"https://www.cookiesbydesign.com{url}"

    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    check = tree.xpath("//label[@for='account-company']")
    if check:
        return parse_corp(tree, page_url)
    else:
        return parse_frach(tree, page_url)


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
