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


def get_coords(page_url):
    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)
    text = "".join(tree.xpath("//a[contains(@href, 'maps')]/@href"))

    return get_coords_from_google_url(text)


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


def fetch_data():
    out = []
    locator_domain = "http://jonsmarketplace.com/"
    api_url = "http://jonsmarketplace.com/locations.aspx"
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
    td = tree.xpath("//tr/td[not(@colspan) and .//a]|//tr[1]/td[@colspan='3']")

    for t in td:
        location_name = "".join(
            t.xpath("./div[@class='locationTitle']/a/text()|./div/text()")
        ).strip()

        line = (
            " ".join(
                "".join(
                    t.xpath("./div[@class='locationTitle']/following-sibling::text()")[
                        :2
                    ]
                ).split()
            )
            or "".join(t.xpath("./div[not(@class='locationTitle')]/a/text()")).strip()
        )
        a = usaddress.tag(line, tag_mapping=tag)[0]
        street_address = f"{a.get('address1')} {a.get('address2') or ''}".strip()
        if street_address == "None":
            street_address = "<MISSING>"
        city = a.get("city") or "<INACCESSIBLE>"
        state = a.get("state") or "<INACCESSIBLE>"
        postal = a.get("postal") or "<INACCESSIBLE>"
        country_code = "US"
        store_number = "<MISSING>"
        slug = "".join(t.xpath("./div[@class='locationTitle']/a/@href"))
        if slug:
            page_url = f"{locator_domain}{slug}"
        else:
            page_url = api_url

        phone = "".join(
            t.xpath("./div[not(@class='locationTitle')]/span/text()")
        ).strip()
        if not phone:
            phone = "".join(
                t.xpath("./div[@class='locationTitle']/following-sibling::text()")[-2]
            ).strip()

        if slug:
            latitude, longitude = get_coords(page_url)
        else:
            text = "".join(t.xpath("./div/a/@href"))
            latitude, longitude = get_coords_from_google_url(text)
        location_type = "<MISSING>"
        hours_of_operation = (
            tree.xpath("//*[contains(text(), 'Store Hours')]/text()")[-1].strip()
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
        out.append(row)

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
