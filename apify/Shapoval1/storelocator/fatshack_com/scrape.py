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
    locator_domain = "https://www.fatshack.com"
    page_url = "https://www.fatshack.com/locations"

    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@class="flex-col-locations w-dyn-item"]')
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
    for d in div:
        line = (
            " ".join(
                d.xpath(
                    './/div[@class="flex-col-address-wrapper-locations"]/a[contains(@href, "goo")]//text()'
                )
            )
            .replace("\n", "")
            .strip()
        )
        a = usaddress.tag(line, tag_mapping=tag)[0]
        street_address = f"{a.get('address1')} {a.get('address2')}".replace(
            "None", ""
        ).strip()
        city = "".join(a.get("city")).replace("Â", "").strip()
        postal = "".join(a.get("postal")).replace("Â", "").strip()
        state = "".join(a.get("state")).strip()
        phone = (
            " ".join(
                d.xpath(
                    './/div[@class="flex-col-address-wrapper-locations"]/a[contains(@href, "tel")]//text()'
                )
            )
            or "<MISSING>"
        )
        country_code = "US"
        store_number = "<MISSING>"
        location_name = "".join(
            d.xpath('.//h4[@class="flex-col-heading-locations"]/text()')
        )
        hours_of_operation = (
            " ".join(
                d.xpath(
                    './/div[@class="flex-col-hours-text-locations w-richtext"]/p//text()'
                )
            )
            .replace("\n", "")
            .replace(" â ", "-")
            .replace(" â", ";")
            .replace(" â", "")
            .replace("  Â ", "")
            .replace(" Â ", "")
            .strip()
        )
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        location_type = "<MISSING>"

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
