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

    locator_domain = "https://www.burritopm.com/"
    page_url = "https://www.burritopm.com/contact-us/"
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
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)

    div = tree.xpath('//div[contains(@class,"question")]')
    for d in div:

        location_type = "<MISSING>"
        ad = (
            "".join(
                d.xpath(
                    './/h4[contains(text(), "Address")]/following-sibling::text()[1]'
                )
            )
            .replace("\n", "")
            .strip()
        )
        a = usaddress.tag(ad, tag_mapping=tag)[0]

        street_address = f"{a.get('address1')} {a.get('address2')}".replace(
            "None", ""
        ).strip()
        phone = (
            "".join(
                d.xpath(
                    './/h4[contains(text(), "Contact")]/following-sibling::text()[1]'
                )
            )
            .replace("\n", "")
            .strip()
        )
        if phone.find("or") != -1:
            phone = phone.split("or")[0].strip()
        state = a.get("state")
        postal = a.get("ZipCode")
        country_code = "US"
        location_name = "".join(d.xpath('.//div[@class="title"]//text()'))
        city = a.get("city")
        store_number = "<MISSING>"
        map_link = "".join(d.xpath(".//iframe/@src"))
        latitude = map_link.split("!3d")[1].strip().split("!")[0].strip()
        longitude = map_link.split("!2d")[1].strip().split("!")[0].strip()
        hours_of_operation = " ".join(
            d.xpath('.//following::ul[@class="rl-company-hours"]/li[2]//text()')
        )
        if (
            location_name.find("Naperville on 59th") != -1
            or location_name.find("Lisle") != -1
            or location_name.find("West Chicago") != -1
            or location_name.find("Carol Stream") != -1
            or location_name.find("Glendale Heights") != -1
            or location_name.find("Algonquin") != -1
        ):
            hours_of_operation = (
                hours_of_operation
                + " "
                + " ".join(
                    d.xpath(
                        './/following::div[./div/h3[contains(text(), "Operating")]]/following-sibling::div[1]//ul/li[1]//text()'
                    )
                )
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
