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


def get_address(line):
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

    a = usaddress.tag(line, tag_mapping=tag)[0]
    street_address = f"{a.get('address1')} {a.get('address2') or ''}".strip()
    if street_address == "None":
        street_address = "<MISSING>"
    city = a.get("city") or "<MISSING>"
    state = a.get("state") or "<MISSING>"
    if "." in state:
        state = state.replace(".", "")
    postal = a.get("postal") or "<MISSING>"

    return street_address, city, state, postal


def get_urls():
    coords = dict()
    session = SgRequests()
    r = session.get("https://www.cariloha.com/stores.html")
    tree = html.fromstring(r.text)

    urls = tree.xpath(
        "//h3[@class='store-region' and not(contains(text(), 'MEXICO')) and not(contains(text(), 'CARIBBEAN'))]/following-sibling::ul[@class='region-list'][1]/li/a/@href"
    )
    text = "".join(tree.xpath("//script[contains(text(),'var markers1=')]/text()"))
    text = text.split("var markers1=")[1].split("var messages1=")[0][1:-2].split("},{")

    for t in text:
        lat = t.split("lat:")[1].split(",")[0]
        lng = t.split("lng:")[1].split(",")[0]
        slug = (
            t.split('storeurl:"')[1].split('"')[0].split("/")[-2].replace("stores-", "")
        )
        coords[slug] = (lat, lng)

    return coords, urls


def get_data(url, coords):
    locator_domain = "https://www.cariloha.com/"
    slug = url.replace("/stores/", "")
    page_url = f"https://www.cariloha.com{url}"

    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    location_name = (
        "".join(tree.xpath("//h1/span/text()|//div[@id='scottsdale-info']/text()"))
        .replace("Visit", "")
        .strip()
    )
    line = tree.xpath(
        "//p[contains(text(), 'Address')]/following-sibling::p[1]/text()|//h4[contains(text(), 'Address')]/following-sibling::p[1]/text()"
    )
    line = list(filter(None, [l.strip() for l in line]))
    cnt = 0
    for l in line:
        if l[0].isdigit():
            break
        cnt += 1

    if cnt == len(line) - 1:
        line = ", ".join(line[1:])
    else:
        line = ", ".join(line[cnt:]).replace(", Poipu Shopping Village", "")

    street_address, city, state, postal = get_address(line)
    country_code = "US"
    store_number = "<MISSING>"
    phone = (
        "".join(
            tree.xpath(
                "//p[contains(text(), 'Phone')]/text()|//p[contains(text(), 'Phone')]/a[contains(@href,'tel')]/text()"
            )
        ).strip()
        or "<MISSING>"
    )
    phone = phone.replace("Phone", "").replace("Email", "").replace(":", "").strip()
    if "F" in phone:
        phone = phone.split("F")[0].strip()
    latitude, longitude = coords.get(slug) or ["<MISSING>", "<MISSING>"]
    location_type = "<MISSING>"

    _tmp = []
    hours = tree.xpath(
        "//p[contains(text(), 'Hours')]/following-sibling::p/text()|//h4[contains(text(), 'Hours')]/following-sibling::p/text()|//p[@class='store-info-p' and contains(text(), 'Mon')]/text()"
    )
    hours = list(filter(None, [h.strip() for h in hours]))
    for h in hours:
        if "Sea" in h:
            continue
        if "Contact" in h or "Located" in h or "Follow" in h or "Store" in h:
            break
        _tmp.append(h)

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


def fetch_data():
    out = []
    coords, urls = get_urls()

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_data, url, coords): url for url in urls}
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
