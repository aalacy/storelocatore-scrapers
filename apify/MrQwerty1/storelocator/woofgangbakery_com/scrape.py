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


def get_adr_from_page(page_url):
    r = session.get(page_url)
    tree = html.fromstring(r.text)
    line = " ".join("".join(tree.xpath("//p[@class='addr']//text()")).split())

    return get_address(line)


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
        "OccupancyType": "address2",
        "OccupancyIdentifier": "address2",
        "SubaddressIdentifier": "address2",
        "SubaddressType": "address2",
        "PlaceName": "city",
        "StateName": "state",
        "ZipCode": "postal",
    }

    try:
        a = usaddress.tag(line, tag_mapping=tag)[0]
        street_address = f"{a.get('address1')} {a.get('address2') or ''}".strip()
        if street_address == "None":
            street_address = "<MISSING>"
        city = a.get("city") or "<MISSING>"
        state = a.get("state") or "<MISSING>"
        if state == "New":
            raise usaddress.RepeatedLabelError("", "", "")
        postal = a.get("postal") or "<MISSING>"
    except usaddress.RepeatedLabelError:
        line = line.split(",")
        postal = line.pop().strip()
        state = line.pop().strip()
        city = line.pop().strip()
        street_address = ",".join(line)

    return street_address, city, state, postal


def fetch_data():
    out = []
    locator_domain = "https://woofgangbakery.com/"
    api_url = "https://api.storerocket.io/api/user/7OdJEZD8WE/locations"
    country_code = "US"

    r = session.get(api_url)
    js = r.json()["results"]["locations"]

    for j in js:
        line = j.get("address").replace(", USA", "").replace(", US", "")
        street_address, city, state, postal = get_address(line)
        if len(postal) == 4:
            postal = f"0{postal}"

        store_number = j.get("id") or "<MISSING>"
        page_url = j.get("url") or "<MISSING>"
        location_name = j.get("name")
        phone = j.get("phone") or "<MISSING>"
        latitude = j.get("lat") or "<MISSING>"
        longitude = j.get("lng") or "<MISSING>"
        location_type = "<MISSING>"

        if postal == "<MISSING>":
            street_address, city, state, postal = get_adr_from_page(page_url)

        _tmp = []
        days = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
        for d in days:
            time = j.get(d)
            if not time:
                break
            _tmp.append(f"{d}: {time}")

        hours_of_operation = ";".join(_tmp) or "Coming Soon"

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
    session = SgRequests()
    scrape()
