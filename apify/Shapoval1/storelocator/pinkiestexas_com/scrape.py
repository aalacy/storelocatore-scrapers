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
    locator_domain = "https://pinkiestexas.com"
    page_url = "https://pinkiestexas.com/locations/"

    session = SgRequests()
    r = session.get(page_url)
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
    tree = html.fromstring(r.text)

    divs = tree.xpath(
        "//div[contains(@class,'et_pb_column et_pb_column_1_3')]//div[@class='et_pb_text_inner']"
    )
    for d in divs:
        location_name = d.xpath("./h3/strong/text()|./p[1]/strong/text()")[0]
        adr = d.xpath(".//p[contains(text(), 'Hours:')]/preceding-sibling::p[1]")
        hours = d.xpath(".//p[contains(text(), 'Hours:')]")

        for a, h in zip(adr, hours):
            name = "".join(a.xpath("./strong/text()"))
            hours_of_operation = (
                "".join(h.xpath("./text()")).replace("\n", "").replace("Hours:", "")
            ).replace("â€“", "-")
            b = usaddress.tag(name, tag_mapping=tag)[0]
            block = "".join(a.xpath("./text()[1]"))
            x = usaddress.tag(block, tag_mapping=tag)[0]
            street_address = b.get("address1")
            city = x.get("city")
            postal = x.get("postal")
            state = x.get("state")
            country_code = "US"
            store_number = "<MISSING>"
            phone = "".join(a.xpath(".//text()[2]")).replace("\n", "").strip()
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
