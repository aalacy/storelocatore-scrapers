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
    except usaddress.RepeatedLabelError:
        street_address = line.split(",")[0]
        a = usaddress.tag(",".join(line.split(",")[1:]), tag_mapping=tag)[0]

    city = a.get("city") or "<MISSING>"
    state = a.get("state") or "<MISSING>"
    postal = a.get("postal") or "<MISSING>"

    return street_address, city, state, postal


def fetch_data():
    out = []
    locator_domain = "https://kristoil.com/"
    page_url = "https://kristoil.com/locations/"
    api_url = "https://kristoil.com/wp-content/themes/krist-2020/ajax/map.php"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; rv:78.0) Gecko/20100101 Firefox/78.0",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "en-US,en;q=0.5",
        "Referer": "https://kristoil.com/locations/",
        "X-Requested-With": "XMLHttpRequest",
        "Connection": "keep-alive",
        "TE": "Trailers",
    }

    session = SgRequests()
    r = session.get(api_url, headers=headers)
    js = r.json().values()
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)

    for j in js:
        location_name = j.get("title")
        store_number = j.get("ID")
        phone = j.get("phone") or "<MISSING>"
        _id = phone[-4:]
        a = j.get("location")

        li = tree.xpath(
            f"//li[@class='grid grid--locations grid--one-col-mobile locations-list__list-item' and .//a[contains(text(), '-{_id}')]]"
        )[0]

        line = (
            "".join(
                li.xpath(
                    ".//li[@class='locations-list__phone-number']/preceding-sibling::li[1]/text()"
                )
            )
            .replace(".", "")
            .strip()
        )
        print(line)
        street_address, city, state, postal = get_address(line)
        country_code = "US"
        try:
            latitude = a.get("lat") or "<MISSING>"
            longitude = a.get("lng") or "<MISSING>"
        except:
            latitude, longitude = "<MISSING>", "<MISSING>"
        location_type = "<MISSING>"
        hours_of_operation = "<MISSING>"

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
