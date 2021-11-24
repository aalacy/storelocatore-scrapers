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

    locator_domain = "http://www.cheftk.com"
    urls = [
        "http://www.cheftk.com/tk-shabu-shabu-house-kona.html",
        "http://www.cheftk.com/tk-noodle-house-kona.html",
        "http://www.cheftk.com/lemongrass-express-waikoloa.html",
        "http://www.cheftk.com/gal-bi-808-bbq-mixed-plate.html",
        "http://www.cheftk.com/thep-thai-cuisine-.html",
    ]
    for i in urls:
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
        r = session.get(i, headers=headers)
        tree = html.fromstring(r.text)

        page_url = i
        phone = (
            "".join(
                tree.xpath(
                    '//span[contains(text(), "(")]/text() | //strong[contains(text(), "(")]/text()'
                )
            )
            .replace("Phone", "")
            .replace(":", "")
            .replace("Call", "")
            .strip()
        )
        phone = phone.replace("​    ", "")
        location_name = (
            "".join(
                tree.xpath(
                    '//div[@class="txt "]/div[1]//text() | //div[@class="txt "]/h6[1]//text()'
                )
            )
            .replace("   ", "")
            .strip()
            or "<MISSING>"
        )
        if page_url == "<MISSING>":
            location_name = "".join(tree.xpath('//div[@class="txt "]/p[1]//text()'))
        if page_url.find("808") != -1:
            location_name = "".join(
                tree.xpath(
                    '//div[@class="txt "]/p[1]//strong[@class="editor_color_green"]/text()'
                )
            )
        if page_url.find("thep-thai") != -1:
            location_name = "Thep Thai Cuisine"

        ad = "".join(tree.xpath('//div[@class="txt "]/div[2]//text()')) or "<MISSING>"
        if page_url.find("lemongrass-express-waikoloa.html") != -1:
            ad = (
                "".join(
                    tree.xpath(
                        '//div[@class="txt "]/h6[1]/following-sibling::p[1]//text()'
                    )
                )
                .replace("            ", "")
                .strip()
            )
        if page_url.find("808") != -1:
            ad = (
                "".join(
                    tree.xpath(
                        '//div[@class="txt "]/p[2]//strong[@class="editor_color_green"]/text()'
                    )
                )
                + " "
                + "".join(
                    tree.xpath(
                        '//div[@class="txt "]/p[3]//strong[@class="editor_color_green"]/text()'
                    )
                )
            )
        if page_url.find("thep-thai") != -1:
            ad = (
                "".join(tree.xpath('//div[@class="txt "]/p[1]//text()'))
                .split("Copyright.")[0]
                .strip()
                + " "
                + "".join(tree.xpath('//div[@class="txt "]/p[2]//text()'))
            )
        a = usaddress.tag(ad, tag_mapping=tag)[0]

        street_address = f"{a.get('address1')} {a.get('address2')}".replace(
            "None", ""
        ).strip()
        state = a.get("state") or "<MISSING>"
        postal = a.get("postal") or "<MISSING>"
        country_code = "USA"
        city = a.get("city") or "<MISSING>"
        location_type = "<MISSING>"
        store_number = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"

        hours_of_operation = "<MISSING>"
        if street_address.find("69-201") != -1:
            session = SgRequests()
            r = session.get("http://www.cheftk.com/contact-us.html", headers=headers)
            tree = html.fromstring(r.text)
            hours_of_operation = (
                "".join(
                    tree.xpath(
                        f'//div[./span[contains(text(), "{street_address}")]]/following-sibling::div[./span[contains(text(), "a.m.")]]//text()'
                    )
                )
                .replace(" ", "")
                .strip()
            )
            latitude = (
                "".join(
                    tree.xpath(f'//script[contains(text(), "{street_address}")]/text()')
                )
                .split("lat:")[1]
                .split(",")[0]
                .strip()
            )
            longitude = (
                "".join(
                    tree.xpath(f'//script[contains(text(), "{street_address}")]/text()')
                )
                .split("lng:")[1]
                .split("}")[0]
                .strip()
            )
        if street_address.find("1103") != -1:
            session = SgRequests()
            r = session.get("http://www.cheftk.com/contact-us.html", headers=headers)
            tree = html.fromstring(r.text)
            slug = street_address.split()[0].strip()
            latitude = (
                "".join(tree.xpath(f'//script[contains(text(), "{slug}")]/text()'))
                .split("lat:")[1]
                .split(",")[0]
                .strip()
            )
            longitude = (
                "".join(tree.xpath(f'//script[contains(text(), "{slug}")]/text()'))
                .split("lng:")[1]
                .split("}")[0]
                .strip()
            )
        if street_address.find("75-5722") != -1:
            hours_of_operation = "11:00 a.m. - 9:00 p.m. daily "

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
