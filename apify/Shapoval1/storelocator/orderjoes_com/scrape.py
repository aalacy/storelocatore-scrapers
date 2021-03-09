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
    locator_domain = "https://orderjoes.com/"
    api_url = (
        "https://orderjoes.com/wp-content/themes/understrap-child/locations_data.php"
    )

    session = SgRequests()
    r = session.get(api_url)
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
    js = r.json()
    for j in js.values():
        ad = j.get("address")
        ad = "".join(ad)
        a = usaddress.tag(ad, tag_mapping=tag)[0]
        street_address = j.get("street")
        city = a.get("city")
        postal = a.get("postal") or "<MISSING>"
        state = a.get("state")
        country_code = "US"
        store_number = "<MISSING>"
        location_name = "".join(j.get("name"))
        phone = "".join(j.get("phone")) or "<MISSING>"
        if phone.find("JOES") != -1:
            phone = phone.replace("JOES", "")
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        location_type = "<MISSING>"
        hours = j.get("hours")
        hours = html.fromstring(hours)
        hours_of_operation = hours.xpath("//*/text()")
        hours_of_operation = list(filter(None, [a.strip() for a in hours_of_operation]))
        hours_of_operation = "".join(hours_of_operation)
        if hours_of_operation.find("Online") != -1:
            hours_of_operation = hours_of_operation.split("Online")[0]
        if hours_of_operation.find("COMING SOON") != -1:
            hours_of_operation = "COMING SOON"
            street_address = "<MISSING>"
        if street_address.find("402") != -1:
            city = "St Salem"
        page_url = "https://orderjoes.com/locations/"
        session = SgRequests()
        r = session.get(page_url)
        tree = html.fromstring(r.text)
        block = tree.xpath('//div[@class="marker"]')
        for b in block:
            address = "".join(b.xpath('.//p[@class="address"]/text()'))
            aa = usaddress.tag(address, tag_mapping=tag)[0]
            subsity = aa.get("city")
            if subsity == city:
                latitude = "".join(b.xpath(".//a/@data-lat"))
                longitude = "".join(b.xpath(".//a/@data-lng"))

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
