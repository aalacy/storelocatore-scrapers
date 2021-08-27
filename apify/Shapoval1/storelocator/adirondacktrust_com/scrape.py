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

    locator_domain = "https://www.adirondacktrust.com"
    api_url = "https://www.adirondacktrust.com/ABOUT/Locations"
    session = SgRequests()
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

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath("//div[./h4/strong]")
    for d in div:
        ad = d.xpath(".//text()")
        ad = list(filter(None, [a.strip() for a in ad]))
        slug = "".join(d.xpath(".//a/@href"))
        page_url = f"{locator_domain}{slug}"

        location_name = "".join(ad[0]).strip()
        adr = "".join(ad).split("Address:")[1].split("VIEW")[0].strip()
        a = usaddress.tag(adr, tag_mapping=tag)[0]

        street_address = f"{a.get('address1')} {a.get('address2')}".replace(
            "None", ""
        ).strip()
        state = a.get("state") or "<MISSING>"
        postal = a.get("postal") or "<MISSING>"
        country_code = "US"
        city = a.get("city") or "<MISSING>"
        location_type = "".join(
            d.xpath(
                f'.//preceding::span[contains(text(), "{street_address}")]/preceding-sibling::span[@title="category"]/text()'
            )
        )
        store_number = "<MISSING>"
        latitude = "".join(
            d.xpath(
                f'.//preceding::span[contains(text(), "{street_address}")]/following-sibling::span[@title="lat"]/text()'
            )
        )
        longitude = "".join(
            d.xpath(
                f'.//preceding::span[contains(text(), "{street_address}")]/following-sibling::span[@title="lng"]/text()'
            )
        )
        try:
            phone = "".join(ad).split("Phone:")[1].split("Address")[0].strip()
        except:
            phone = "<MISSING>"

        session = SgRequests()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)
        hours_of_operation = tree.xpath(
            '//strong[text()="Lobby"]/following-sibling::text() | //h2[text()="Hours of Operation: "]/following-sibling::p[1]/text()'
        )
        hours_of_operation = list(filter(None, [a.strip() for a in hours_of_operation]))
        hours_of_operation = " ".join(hours_of_operation) or "<MISSING>"

        if hours_of_operation == "<MISSING>":
            try:
                hours_of_operation = (
                    "".join(ad).split("Hours:")[1].split("Address")[0].strip()
                )
            except:
                hours_of_operation = "<MISSING>"
        hours_of_operation = (
            hours_of_operation.replace("YMCA hours", "<MISSING>")
            .replace("Care Center hours", "<MISSING>")
            .replace("Library hours", "<MISSING>")
            .replace("Mall hours", "<MISSING>")
            .strip()
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
