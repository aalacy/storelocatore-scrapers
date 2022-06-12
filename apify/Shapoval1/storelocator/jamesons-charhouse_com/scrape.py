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

    locator_domain = "https://jamesons-charhouse.com"
    api_url = "https://jamesons-charhouse.com/the-jamesons-experience/"
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
    tree = html.fromstring(r.text)
    div = tree.xpath("//h3[./a]/a")
    for d in div:

        page_url = "".join(d.xpath(".//@href"))
        location_type = "<MISSING>"
        session = SgRequests()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)

        ad = (
            " ".join(tree.xpath('//div[./p/strong[text()="ADDRESS"]]/p[2]/text()'))
            .replace("\n", "")
            .strip()
        )
        a = usaddress.tag(ad, tag_mapping=tag)[0]
        location_name = "".join(
            tree.xpath('//div[./p/strong[text()="ADDRESS"]]/preceding::h3[1]/text()')
        )
        street_address = f"{a.get('address1')} {a.get('address2')}".replace(
            "None", ""
        ).strip()

        state = a.get("state") or "<MISSING>"
        postal = a.get("postal") or "<MISSING>"
        if street_address.find("671") != -1:
            postal = "29909"

        country_code = "US"
        city = a.get("city") or "<MISSING>"
        store_number = "<MISSING>"
        map_link = "".join(tree.xpath("//iframe/@src"))
        latitude = map_link.split("!3d")[1].strip().split("!")[0].strip()
        longitude = map_link.split("!2d")[1].strip().split("!")[0].strip()
        phone = (
            "".join(
                tree.xpath(
                    '//div[./p/strong[text()="ADDRESS"]]//a[contains(@href, "tel")]/text()'
                )
            )
            .replace("Call us at", "")
            .strip()
        )
        hours_of_operation = (
            " ".join(
                tree.xpath('//p[./strong[text()="HOURS"]]/following-sibling::p//text()')
            )
            .replace("\n", "")
            .strip()
        )
        if hours_of_operation.find("*") != -1:
            hours_of_operation = hours_of_operation.split("*")[0].strip()
        if street_address.find("1001") != -1:
            hours_of_operation = hours_of_operation.replace(
                " Sat: 3:00 – 8:30pm Sun: 3:00 – 8:00pm", ""
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
