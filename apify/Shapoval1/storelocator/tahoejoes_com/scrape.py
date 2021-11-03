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

    locator_domain = "https://tahoejoes.com"
    api_url = "https://tahoejoes.com/wp-content/plugins/superstorefinder-wp/ssf-wp-xml.php?wpml_lang=&t=1626126491561"
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

    tree = html.fromstring(r.content)
    div = tree.xpath("//locator/store/item")

    for d in div:
        page_url = "https://tahoejoes.com/locations/"
        location_name = "".join(d.xpath(".//location/text()")).replace("&#44;", ",")
        ad = (
            "".join(d.xpath(".//address/text()"))
            .replace("&#44;", ",")
            .replace("Central Coast Plaza Shopping Center,", "")
            .strip()
        )
        a = usaddress.tag(ad, tag_mapping=tag)[0]
        location_type = "<MISSING>"
        street_address = (
            f"{a.get('address1')} {a.get('address2')}".replace("None", "")
            .replace("The Marketplace", "")
            .replace("HomeTown Plaza", "")
            .strip()
        )
        state = a.get("state") or "<MISSING>"
        postal = a.get("postal") or "<MISSING>"
        country_code = "US"
        city = a.get("city") or "<MISSING>"
        store_number = "".join(d.xpath(".//sortord/text()"))
        latitude = "".join(d.xpath(".//latitude/text()"))
        longitude = "".join(d.xpath(".//longitude/text()"))
        phone = "".join(d.xpath(".//telephone/text()"))
        hours_of_operation = "".join(d.xpath(".//description/text()"))
        a = html.fromstring(hours_of_operation)
        hours_of_operation = " ".join(a.xpath("//*//text()")).replace("\n", "").strip()
        if hours_of_operation.find("Take-Out") != -1:
            hours_of_operation = hours_of_operation.split("Take-Out")[0].strip()
        if location_name.find("Temp. Closed") != -1:
            location_type = "Temporarily Closed"
        location_name = location_name.replace(
            "(Temp. Closed Until Further Notice)", ""
        ).strip()
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
