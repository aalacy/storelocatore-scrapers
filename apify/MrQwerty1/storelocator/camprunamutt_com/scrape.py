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


def get_phone_hoo_coords(page_url):
    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    line = tree.xpath("//p[@class='campAddress']/text()")
    line = list(filter(None, [l.strip() for l in line]))
    if not line:
        return "<MISSING>", "<MISSING>", ("<MISSING>", "<MISSING>")
    phone = line[-1].replace("phone", "").replace(":", "").strip()

    _tmp = []
    hours = tree.xpath("//h4[text()='Business Hours']/following-sibling::p/text()")
    hours = list(filter(None, [h.strip() for h in hours]))
    for h in hours:
        _tmp.append(h)
        if "Sunday" in h:
            break

    hours_of_operation = ";".join(_tmp) or "<MISSING>"

    try:
        text = "".join(tree.xpath("//iframe[contains(@src, 'google')]/@src"))
        latitude = text.split("!3d")[1].strip().split("!")[0].strip()
        longitude = text.split("!2d")[1].strip().split("!")[0].strip()
        coords = (latitude, longitude)
    except IndexError:
        coords = ("<MISSING>", "<MISSING>")

    return phone, hours_of_operation, coords


def fetch_data():
    out = []
    locator_domain = "https://camprunamutt.com/"
    api_url = "https://camprunamutt.com/locations.php"

    session = SgRequests()
    r = session.get(api_url)
    tree = html.fromstring(r.text)
    divs = tree.xpath("//div[@class='location' and .//div[@class='locationWebsite']]")
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

    for d in divs:
        location_name = "".join(d.xpath("./div[@class='locationName']/text()")).strip()
        line = "".join(d.xpath("./address/text()")).strip()
        a = usaddress.tag(line, tag_mapping=tag)[0]
        street_address = f"{a.get('address1')} {a.get('address2') or ''}".strip()
        if street_address == "None":
            street_address = "<MISSING>"
        city = a.get("city") or "<INACCESSIBLE>"
        state = a.get("state") or "<INACCESSIBLE>"
        postal = a.get("postal") or "<INACCESSIBLE>"
        country_code = "US"
        store_number = "<MISSING>"
        slug = "".join(d.xpath("./div[@class='locationWebsite']/a/@href"))
        page_url = f"{locator_domain}{slug}"
        location_type = "<MISSING>"
        phone, hours_of_operation, coords = get_phone_hoo_coords(page_url)
        latitude, longitude = coords

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
