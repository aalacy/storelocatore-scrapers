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

    a = usaddress.tag(line, tag_mapping=tag)[0]
    street_address = f"{a.get('address1')} {a.get('address2') or ''}".strip()
    if street_address == "None":
        street_address = "<MISSING>"
    city = a.get("city") or "<MISSING>"
    state = a.get("state") or "<MISSING>"
    postal = a.get("postal") or "<MISSING>"

    return street_address, city, state, postal


def get_states():
    session = SgRequests()
    r = session.get("https://regymenfitness.com/locations/")
    tree = html.fromstring(r.text)

    return tree.xpath("//div[@class='et_pb_text_inner']/h3/text()")


def get_coords_from_embed(text):
    try:
        latitude = text.split("!3d")[1].strip().split("!")[0].strip()
        longitude = text.split("!2d")[1].strip().split("!")[0].strip()
    except IndexError:
        latitude, longitude = "<MISSING>", "<MISSING>"

    return latitude, longitude


def fetch_data():
    out = []
    states = get_states()
    locator_domain = "https://regymenfitness.com/"

    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }

    for state in states:
        url = f"https://regymenfitness.com/{state}"
        r = session.get(url, headers=headers)
        tree = html.fromstring(r.text)
        divs = tree.xpath(
            "//div[contains(@class, 'et_pb_column et_pb_column_1_3') and .//iframe]"
        )

        for d in divs:
            page_url = "".join(d.xpath(".//a[contains(text(), 'View ')]/@href"))
            location_name = "".join(d.xpath(".//h2/text()")).strip()
            line = " ".join(
                "".join(
                    d.xpath(".//div[@class='et_pb_blurb_description']/text()")
                ).split()
            )

            if "Canada" not in line:
                street_address, city, state, postal = get_address(line)
                country_code = "US"
            else:
                line = line.split(",")
                street_address = line.pop(0).strip()
                city = line.pop(0).strip()
                line = line.pop(0)
                state = line.split()[0].strip()
                postal = line.replace(state, "").strip()
                country_code = "CA"
            store_number = "<MISSING>"
            phone = (
                "".join(
                    d.xpath(".//h4[@class='et_pb_module_header']/span/text()")
                ).strip()
                or "<MISSING>"
            )
            text = "".join(d.xpath(".//iframe/@src"))
            latitude, longitude = get_coords_from_embed(text)
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
