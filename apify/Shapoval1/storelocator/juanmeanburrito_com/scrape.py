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
    locator_domain = "https://www.juanmeanburrito.com"
    page_url = "https://www.juanmeanburrito.com/locations/"

    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)
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
    div = tree.xpath(
        "//div[contains(@class, 'et_pb_row_inner et_pb_row_inner')  and contains(.//div/p/strong/text(), 'Fax')]"
    )
    for d in div:
        line = "".join(d.xpath('.//div[@class="et_pb_text_inner"]/h3/text()'))
        a = usaddress.tag(line, tag_mapping=tag)[0]
        street_address = f"{a.get('address1')} {a.get('address2')}".replace(
            "None", ""
        ).strip()
        city = "".join(a.get("city")).strip()
        postal = a.get("postal") or "<MISSING>"
        state = "".join(a.get("state")).strip()
        phone = (
            "".join(d.xpath('.//div[@class="et_pb_text_inner"]/p/text()[1]'))
            .replace("|", "")
            .strip()
        )
        hours_of_operation = "<MISSING>"
        country_code = "US"
        store_number = "<MISSING>"
        location_name = city
        ll = "".join(d.xpath('.//div[@class="et_pb_text_inner"]/p/iframe/@src'))
        ll = ll.split("!2d")[1].split("!2m")[0].replace("!3d", ",")
        latitude = ll.split(",")[1]
        longitude = ll.split(",")[0]
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
