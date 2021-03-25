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
    postal = a.get("postal") or "<MISSING>"

    return street_address, city, state, postal


def get_coords_from_google_url(url):
    try:
        if url.find("ll=") != -1:
            latitude = url.split("ll=")[1].split(",")[0]
            longitude = url.split("ll=")[1].split(",")[1].split("&")[0]
        else:
            latitude = url.split("@")[1].split(",")[0]
            longitude = url.split("@")[1].split(",")[1]
    except IndexError:
        latitude, longitude = "<MISSING>", "<MISSING>"

    return latitude, longitude


def get_coords_from_embed(text):
    try:
        latitude = text.split("!3d")[1].strip().split("!")[0].strip()
        longitude = text.split("!2d")[1].strip().split("!")[0].strip()
    except IndexError:
        latitude, longitude = "<MISSING>", "<MISSING>"

    return latitude, longitude


def fetch_data():
    out = []
    locator_domain = "https://m.mrmac.com"
    page_url = "https://m.mrmac.com/pages/locations"
    location_type = "<MISSING>"

    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)
    divs = tree.xpath("//div[@class='information' and ./div[@class='row']]")

    for d in divs:
        location_name = "".join(d.xpath('.//p[@class="name"]/text()')).strip()
        line = " ".join(d.xpath('.//div[@class="address"]/a/text()'))

        street_address, city, state, postal = get_address(line)
        if street_address.find("62") != -1:
            street_address = " ".join(line.split(",")[0].split()[:-2])
            city = " ".join(line.split(",")[0].split()[-2:])
            state = "".join(line.split(",")[1].split()[0])
        country_code = "US"
        store_number = "<MISSING>"

        phone = (
            "".join(
                d.xpath(
                    './/div[@class="phone"]/text()[1]|.//div[@class="address"]/text()'
                )
            )
            .replace('"Phone:"', "")
            .strip()
        )
        if "Fax" in phone:
            phone = phone.split("Fax")[0].strip()

        text = "".join(d.xpath(".//p/iframe/@src"))
        if "ll=" not in text:
            latitude, longitude = get_coords_from_embed(text)
        else:
            latitude, longitude = get_coords_from_google_url(text)
        hours_of_operation = " ".join(
            " ".join(d.xpath('.//div[@class="hours"]//text()'))
            .replace("Open", "")
            .split()
        ).replace("PM", "PM;")

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
