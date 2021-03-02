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
    locator_domain = "https://www.texastooltraders.com"
    page_url = "https://www.texastooltraders.com/store-location"

    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.content)
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
        '//div[@class="clearfix white"]/br/preceding-sibling::p | //div[@class="clearfix white"]/br/following-sibling::p'
    )

    for j in div:
        ad = " ".join(j.xpath("./text()[1]"))
        a = usaddress.tag(ad, tag_mapping=tag)[0]
        street_address = f"{a.get('address1')} {a.get('address2')}".replace(
            "None", ""
        ).strip()
        city = "".join(a.get("city"))
        if city.find("Weimar") != -1:
            continue

        postal = "".join(a.get("postal"))
        state = a.get("state")
        phone = "".join(j.xpath("./text()[2]"))
        hours_of_operation = (
            "".join(j.xpath(".//text()[3]")) + " " + "".join(j.xpath(".//text()[4]"))
        )
        if city.find("Houston") != -1:
            hours_of_operation = (
                "".join(j.xpath("//p/span[2]/text()"))
                + " "
                + "".join(j.xpath(".//text()[3]"))
                + " "
                + "".join(j.xpath(".//text()[4]"))
            )
        country_code = "US"
        store_number = "<MISSING>"
        location_name = "<MISSING>"
        if postal.find("77") != -1:
            location_name = "Houston Area Locations"
        if phone.find("210") != -1:
            location_name = "San Antonio Area Stores"
        if phone.find("817") != -1 or phone.find("972") != -1:
            location_name = "Dallas/Fort Worth Area Stores"
        if phone.find("512") != -1:
            location_name = "Austin Area Stores"
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
