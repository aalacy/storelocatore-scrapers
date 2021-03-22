import csv
import usaddress

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


def get_hours(page_url):
    li = []
    _tmp = []
    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)
    ul = tree.xpath("//div[@class='full-content']/ul")

    for u in ul:
        text = "".join(u.xpath("./preceding-sibling::*[1]//text()"))
        if "lobby" in text.lower():
            li = u.xpath("./li")
            break

    for l in li:
        text = " ".join("".join(l.xpath(".//text()")).split())
        if ":" in text:
            _tmp.append(text)

    if not _tmp:
        lines = tree.xpath(
            "//div[@class='full-content']/p[./strong[contains(text(), 'Lobby')]]/text()"
        )
        lines = list(filter(None, [l.strip() for l in lines]))
        _tmp = lines

    if not _tmp:
        _tmp = tree.xpath(
            "//div[@class='full-content']/p[./strong[contains(text(), 'Lobby')]]/following-sibling::*[1]//text()"
        )

    if not _tmp:
        text = tree.xpath("//div[@class='full-content']/p/text()")
        for t in text:
            if "Monday" in t:
                _tmp.append(t.strip())

    return ";".join(_tmp) or "<MISSING>"


def fetch_data():
    out = []
    locator_domain = "https://www.washtrust.com/"
    api_url = "https://www.washtrust.com/about/locations"
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

    session = SgRequests()
    r = session.get(api_url)
    tree = html.fromstring(r.text)
    li = tree.xpath("//div[@class='location-results']/ul/li")
    coords = dict()

    text = "".join(
        tree.xpath("//script[contains(text(), 'smartMap.createMarker(')]/text()")
    )
    text = text.split("scrollwheel")[1].split("createInfoWindow")[0].split("\n")
    for t in text:
        if "createMarker" in t:
            v = eval(t.split("smartMap.coords")[1].split(',"')[0])
            k = t.split('"title":"')[1].split('"})')[0]
            coords[k] = v

    for l in li:
        location_name = "".join(l.xpath("./strong/text()|./a/text()")).strip()
        line = "".join(l.xpath("./span[@class='address']/text()")).strip()
        a = usaddress.tag(line, tag_mapping=tag)[0]
        street_address = f"{a.get('address1')} {a.get('address2') or ''}".strip()
        if street_address == "None":
            street_address = "<MISSING>"
        city = a.get("city") or "<INACCESSIBLE>"
        state = a.get("state") or "<INACCESSIBLE>"
        postal = a.get("postal") or "<INACCESSIBLE>"
        country_code = "US"
        store_number = "<MISSING>"
        page_url = "".join(l.xpath(".//a[@class='arrow-link']/@href")) or api_url
        phone = "".join(l.xpath("./span[@class='phone']/text()")).strip() or "<MISSING>"
        latitude, longitude = coords.get(location_name) or ["<MISSING>", "<MISSING>"]
        if "ATM" in location_name:
            location_type = "ATM"
        else:
            location_type = "Branch"

        if page_url != api_url:
            hours_of_operation = get_hours(page_url)
        else:
            hours_of_operation = "<MISSING>"
        if "Opening" in location_name:
            hours_of_operation = "Coming Soon"

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
        out.append(row)

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
