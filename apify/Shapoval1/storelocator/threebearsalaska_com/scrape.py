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
    locator_domain = "https://threebearsalaska.com/"
    api_url = "https://threebearsalaska.com/#"
    session = SgRequests()
    r = session.get(api_url)
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

    div = tree.xpath('//li[@id="menu-item-5072"]/ul/li/a')
    for d in div:

        page_url = "".join(d.xpath(".//@href"))
        session = SgRequests()
        r = session.get(page_url)
        tree = html.fromstring(r.text)

        ad = (
            " ".join(
                tree.xpath(
                    '//p[./strong[contains(text(), "Physical Address")]]/text() | //h2[contains(text(), "Physical and Mailing Address")]/following-sibling::p[1]/text() | //h2[./strong[contains(text(), "Physical and Mailing Address")]]/following-sibling::p[1]/text() | //h2[contains(text(), "Physical Address")]/following-sibling::p[1]/text()'
                )
            )
            .replace("\n", "")
            .strip()
        )
        if not ad:
            ad = " ".join(
                tree.xpath(
                    '//p[./strong[contains(text(), "Physical Address")]]/following-sibling::p[1]/text()'
                )
            )

        a = usaddress.tag(ad, tag_mapping=tag)[0]

        street_address = f"{a.get('address1')} {a.get('address2')}".replace(
            "None", ""
        ).strip()
        city = a.get("city") or "<MISSING>"
        state = a.get("state") or "<MISSING>"
        postal = a.get("postal") or "<MISSING>"
        if ad.find("Mile") != -1:
            street_address = " ".join(ad.split(",")[0].split()[:-1]).strip()
            city = ad.split(",")[0].split()[-1].strip()
            state = ad.split(",")[1].split()[0].strip()
            postal = ad.split(",")[1].split()[-1].strip()
        country_code = "US"
        store_number = "<MISSING>"
        location_name = "".join(tree.xpath("//h1/text()"))

        phone = (
            "".join(
                tree.xpath(
                    '//strong[contains(text(), "Telephone:")]/following-sibling::text()[1]'
                )
            ).strip()
            or "<MISSING>"
        )
        if phone == "<MISSING>":
            phone = (
                "".join(tree.xpath('//p[contains(text(), "Telephone")]/text()[1]'))
                .replace("Telephone:", "")
                .strip()
            )
        if phone.count("-") > 2:
            phone = phone.split()[0].strip()
        ll = "".join(tree.xpath('//script[contains(text(), "centerLat")]/text()'))
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        if ll:
            latitude = ll.split("centerLat")[1].split('Number("')[1].split('");')[0]
            longitude = ll.split("centerLng")[1].split('Number("')[1].split('");')[0]
        location_type = "<MISSING>"
        hours_of_operation = (
            " ".join(
                tree.xpath(
                    '//p[./strong[contains(text(), "Main Store Hours Of Operation")]]/following-sibling::p[position()<3]/text() | //h3[./strong[text()="Store Hours"]]/text() | //p[./strong[contains(text(), "Store Hours")]]/text()'
                )
            )
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
        if hours_of_operation == "<MISSING>":
            hours_of_operation = (
                " ".join(
                    tree.xpath(
                        '//p[./strong[contains(text(), "Store Hours:")]]/following-sibling::p[position()<3]/text() | //h2[contains(text(), "Hours of ")]/following-sibling::p[1]/text()'
                    )
                )
                .replace("\n", "")
                .strip()
            )
        hours_of_operation = (
            hours_of_operation.replace(":  ", "").replace(": M", "M").strip()
        )
        if street_address.find("3457") != -1:
            hours_of_operation = (
                hours_of_operation
                + " "
                + "".join(
                    tree.xpath(
                        '//h3[./strong[contains(text(), "Store Hours")]]/following-sibling::h3[1]/text()'
                    )
                )
                .replace("\n", "")
                .strip()
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
