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


def get_coords_from_embed(page_url):
    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)
    text = "".join(tree.xpath("//iframe/@src"))

    try:
        latitude = text.split("!3d")[1].strip().split("!")[0].strip()
        longitude = text.split("!2d")[1].strip().split("!")[0].strip()
    except IndexError:
        latitude, longitude = "<MISSING>", "<MISSING>"

    return latitude, longitude


def fetch_data():
    out = []
    locator_domain = "https://800degrees.com/"
    api_url = "https://800degrees.com/locations/"

    session = SgRequests()
    r = session.get(api_url)
    tree = html.fromstring(r.text)
    divs = tree.xpath(
        "//div[@class='elementor-widget-wrap' and .//*[text()='MENUS'] and ./div[contains(@class, 'elementor-element')]]"
    )

    for d in divs:
        location_name = "".join(d.xpath(".//h3/text()"))
        if "(" in location_name:
            continue
        phone = (
            "".join(d.xpath(".//a[contains(@href, 'tel')]//text()")).strip()
            or "<MISSING>"
        )
        line = d.xpath(".//h4[text()='Address']/following-sibling::div[1]/text()")
        line = " ".join(list(filter(None, [l.strip() for l in line]))).replace(
            "\n", " "
        )

        street_address, city, state, postal = get_address(line)
        if "None" in street_address:
            street_address = "800° Chicago"
            city = "Chicago"
        if "Tom" in line:
            street_address = line.split(city)[0].strip()
        country_code = "US"
        store_number = "<MISSING>"
        page_url = "".join(d.xpath(".//a[@class='view-locate']/@href")) or api_url
        if page_url.startswith("/"):
            page_url = f"https://800degrees.com{page_url}"

        if page_url != api_url:
            latitude, longitude = get_coords_from_embed(page_url)
        else:
            latitude, longitude = "<MISSING>", "<MISSING>"

        location_type = "<MISSING>"
        hours = d.xpath(
            ".//h4[contains(text(), 'Hours')]/following-sibling::div//text()|.//h4[contains(text(), 'Hours')]/following-sibling::h4//text()"
        )
        hours = list(filter(None, [h.strip() for h in hours]))
        if "View" in hours[-1]:
            hours.pop()

        if not hours:
            hours_of_operation = "<MISSING>"
        elif "coming" in "".join(hours).lower():
            hours_of_operation = "Coming Soon"
        elif "temporarily" in "".join(hours).lower():
            hours_of_operation = "Temporarily Closed"
        else:
            hours_of_operation = (
                " ".join(hours).replace("PM", "PM;").replace("12:00 PM;", "12:00 PM")
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
        out.append(row)

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
