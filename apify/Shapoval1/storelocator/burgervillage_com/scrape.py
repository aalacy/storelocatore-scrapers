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

    locator_domain = "https://www.burgervillage.com/"
    page_url = "https://www.burgervillage.com/our-locations/"
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
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[contains(@class, "neck_addsec")]')
    for d in div:

        location_name = "".join(d.xpath(".//h3/text()"))
        location_type = "<MISSING>"
        phone = (
            "".join(d.xpath('.//p[contains(text(), "Phone")]/text()'))
            .replace("Phone:", "")
            .strip()
        )
        ad = (
            " ".join(
                d.xpath(
                    './/p[@class="mb-0"]/text() | .//p[contains(text(), "901")]//text()'
                )
            )
            .replace("\n", "")
            .replace("Address:", "")
            .strip()
        )

        street_address = "<MISSING>"
        state = "<MISSING>"
        postal = "<MISSING>"
        country_code = "<MISSING>"
        city = "<MISSING>"

        if ad.find("6187") == -1:
            a = usaddress.tag(ad, tag_mapping=tag)[0]
            street_address = f"{a.get('address1')} {a.get('address2')}".replace(
                "None", ""
            ).strip()
            state = a.get("state")
            postal = a.get("postal")
            country_code = "US"
            city = a.get("city")
        if ad.find("6187") != -1:
            street_address = ad.split(",")[0].strip()
            state = ad.split(",")[2].split()[0]
            postal = " ".join(ad.split(",")[2].split()[1:])
            country_code = "CA"
            city = ad.split(",")[1].strip()
        store_number = "<MISSING>"
        latitude, longitude = "<MISSING>", "<MISSING>"
        hours_of_operation = (
            " ".join(d.xpath(".//ul/li/text()")).replace("\n", "").strip()
            or "<MISSING>"
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
