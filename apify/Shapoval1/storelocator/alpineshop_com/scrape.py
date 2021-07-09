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

    locator_domain = "https://alpineshop.com/"
    api_url = "https://alpineshop.com/info/locations-and-hours"
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
    r = session.get(api_url, timeout=100)
    tree = html.fromstring(r.text)
    div = tree.xpath('//p[./strong[contains(text(), "Alpine Sho")]]')
    for d in div:

        page_url = "https://www.alpineshop.com/info/locations-and-hours"
        location_name = "".join(d.xpath(".//strong/text()")).replace("\n", "").strip()
        location_type = "<MISSING>"
        ad = (
            "".join(
                d.xpath(
                    './/following-sibling::p[./a[contains(@href, "google")]][1]/text()[1]'
                )
            )
            .replace("\n", "")
            .strip()
        )
        a = usaddress.tag(ad, tag_mapping=tag)[0]
        street_address = f"{a.get('address1')} {a.get('address2')}".replace(
            "None", ""
        ).strip()
        if street_address.find("(") != -1:
            street_address = street_address.split("(")[0].strip()
        phone = (
            "".join(
                d.xpath(
                    './/following-sibling::p[./a[contains(@href, "google")]][1]/text()[2]'
                )
            )
            .replace("\n", "")
            .strip()
        )
        city = a.get("city") or "<MISSING>"
        postal = a.get("postal") or "<MISSING>"
        country_code = "US"
        state = a.get("state") or "<MISSING>"
        store_number = "<MISSING>"
        text = (
            "".join(
                d.xpath(
                    './/following-sibling::p[./a[contains(@href, "google")]][1]/a/@href'
                )
            )
            .replace("\n", "")
            .strip()
        )
        try:
            if text.find("ll=") != -1:
                latitude = text.split("ll=")[1].split(",")[0]
                longitude = text.split("ll=")[1].split(",")[1].split("&")[0]
            else:
                latitude = text.split("@")[1].split(",")[0]
                longitude = text.split("@")[1].split(",")[1]
        except IndexError:
            latitude, longitude = "<MISSING>", "<MISSING>"
        hours_of_operation = d.xpath(
            './/following-sibling::p[./strong[contains(text(), "Regular Hours:")]][1]/text()'
        )
        hours_of_operation = list(filter(None, [a.strip() for a in hours_of_operation]))
        hours_of_operation = " ".join(hours_of_operation).replace("\\xa0", "").strip()

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
