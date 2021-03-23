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
    locator_domain = "https://chopstop.com"
    api_url = "https://468915-1485718-2-raikfcquaxqncofqfm.stackpathdns.com/wp-content/plugins/superstorefinder-wp/ssf-wp-xml.php?wpml_lang=&t=1615019516150"

    session = SgRequests()
    r = session.get(api_url)
    tree = html.fromstring(r.content)
    div = tree.xpath("//item")
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
        ad = d.xpath("./address/text()")
        ad = list(filter(None, [a.strip() for a in ad]))
        ad = "".join(ad).replace("&#44;", ",")
        a = usaddress.tag(ad, tag_mapping=tag)[0]

        street_address = f"{a.get('address1')} {a.get('address2')}".replace(
            "None", ""
        ).strip()
        if street_address.find("750") != -1:
            street_address = street_address + " " + a.get("city").split(")")[0].strip()
        city = a.get("city")
        if city.find(")") != -1:
            city = city.split(")")[1].strip()
        postal = a.get("postal")
        state = a.get("state")
        country_code = "US"
        store_number = "".join(d.xpath(".//sortord/text()"))
        page_url = "https://chopstop.com/locations/"
        location_name = (
            "".join(d.xpath(".//location/text()"))
            .replace("&#44;", ",")
            .replace("Ã±", "n")
        )
        phone = "".join(d.xpath(".//telephone/text()")) or "<MISSING>"
        location_type = "<MISSING>"
        hours_of_operation = "".join(d.xpath(".//description/text()"))
        if hours_of_operation == "":
            hours_of_operation = '<div style="overflow-wrap: break-word;">'
        hours = html.fromstring(hours_of_operation)
        hh = "".join(hours.xpath("//b/text()")).strip() or "<MISSING>"
        hours_of_operation = hh
        if location_name.find("Coming") != -1:
            hours_of_operation = "Coming Soon"
        latitude = "".join(d.xpath(".//latitude/text()"))
        longitude = "".join(d.xpath(".//longitude/text()"))
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
