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


def fetch_data():
    out = []
    locator_domain = "https://ptsolutions.com/"
    api_url = "https://ptsolutions.com/clinic-search-results-2/?per_page=5000&form=1"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:83.0) Gecko/20100101 Firefox/83.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "uk-UA,uk;q=0.8,en-US;q=0.5,en;q=0.3",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "TE": "Trailers",
    }

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
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    li = tree.xpath("//li[contains(@id, 'single-post')]")

    for l in li:
        line = (
            "".join(l.xpath(".//div[@class='wppl-address']/text()"))
            .replace(", USA", "")
            .strip()
        )
        a = usaddress.tag(line, tag_mapping=tag)[0]

        street_address = f"{a.get('address1')} {a.get('address2') or ''}".strip()
        if street_address == "None":
            street_address = "<MISSING>"
        city = a.get("city") or "<MISSING>"
        state = a.get("state") or "<MISSING>"
        postal = a.get("postal") or "<MISSING>"
        country_code = "US"
        store_number = l.xpath("./@id")[0].split("-")[-1]
        page_url = "".join(l.xpath(".//h2/a/@href"))
        location_name = "".join(l.xpath(".//h2/a/text()")).split(")")[1].strip()
        phone = (
            "".join(l.xpath(".//a[contains(@href, 'tel')]/text()")).strip()
            or "<MISSING>"
        )
        try:
            loc = (
                "".join(l.xpath(".//a[@class='gmw-get-directions']/@href"))
                .split("&daddr=")[1]
                .split("&")[0]
            )
            latitude = loc.split(",")[0] or "<MISSING>"
            longitude = loc.split(",")[1] or "<MISSING>"
        except:
            latitude = "<MISSING>"
            longitude = "<MISSING>"
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
