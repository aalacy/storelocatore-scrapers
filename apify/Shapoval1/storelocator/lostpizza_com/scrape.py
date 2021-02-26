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
    locator_domain = "https://lostpizza.com"
    api_url = "https://lostpizza.com/locations/"

    session = SgRequests()
    r = session.get(api_url)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@class="col-md-4"]')
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
        ad = (
            " ".join(
                d.xpath(
                    './/div[@class="location-data address"]/div[@class="location-meta"]//text()'
                )
            )
            .replace("\n", "")
            .strip()
        )
        a = usaddress.tag(ad, tag_mapping=tag)[0]
        street_address = f"{a.get('address1')} {a.get('address2')}".replace(
            "None", ""
        ).strip()
        city = a.get("city")
        postal = a.get("postal") or "<MISSING>"
        state = a.get("state")
        country_code = "US"
        store_number = "<MISSING>"
        page_url = "".join(d.xpath('.//a[contains(@href, "locations")]/@href'))
        location_name = (
            "".join(d.xpath('.//h1[@class="the-title"]/text()'))
            .replace("\n", "")
            .strip()
        )
        if location_name.find("Benton") != -1:
            city = location_name.split(",")[0].strip()
            state = location_name.split(",")[1].strip()
        if location_name.find("Tupelo on Main") != -1:
            city = location_name.split(",")[0].split()[0].strip()
            state = location_name.split(",")[1].strip()
        phone = (
            "".join(
                d.xpath(
                    './/div[@class="location-data phone"]/div[@class="location-meta"]//text()'
                )
            )
            .replace("\n", "")
            .strip()
        )
        location_type = "<MISSING>"
        hours_of_operation = (
            "".join(
                d.xpath(
                    './/div[@class="location-data hours"]/div[@class="location-meta"]//text()'
                )
            )
            .replace("\n", "")
            .strip()
        )
        session = SgRequests()
        r = session.get(page_url)
        block = html.fromstring(r.text)
        ll = "".join(block.xpath('//div[@class="maparea"]/p/iframe/@src'))
        ll = ll.split("!2d")[1].split("!2m")[0].replace("!3d", ",")
        latitude = ll.split(",")[1]
        longitude = ll.split(",")[0]
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
