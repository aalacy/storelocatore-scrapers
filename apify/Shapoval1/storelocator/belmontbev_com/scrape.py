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

    locator_domain = "https://www.belmontbev.com"
    page_url = "https://www.belmontbev.com/locations/"
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
    div = tree.xpath(
        "//div[contains(@class, 'has_eae_slider elementor-column elementor-col-33')]/div/div[./div//a[contains(text(), 'Get')]]"
    )

    for d in div:

        location_name = "".join(
            d.xpath('.//h3[@class="elementor-image-box-title"]/text()')
        )
        location_type = "<MISSING>"
        adr = (
            " ".join(d.xpath('.//a[contains(text(), "Get")]/preceding-sibling::text()'))
            .replace("\n", "")
            .strip()
        )
        if adr.find("Phone") != -1:
            adr = adr.split("Phone")[0].strip()
        adr = (
            adr.replace("(", " ")
            .replace(")", " ")
            .replace("AveSouth", "Ave South")
            .strip()
        )

        a = usaddress.tag(adr, tag_mapping=tag)[0]
        street_address = f"{a.get('address1')} {a.get('address2')}".replace(
            "None", ""
        ).strip()
        phone = (
            "".join(
                d.xpath('.//a[contains(text(), "Get")]/preceding-sibling::text()[1]')
            )
            .replace("Phone:", "")
            .strip()
        )
        if phone.find("3320") != -1:
            phone = phone.split()[-1]

        state = a.get("state") or "<MISSING>"
        postal = a.get("postal") or "<MISSING>"
        country_code = "US"
        city = a.get("city") or "<MISSING>"
        if street_address.find("1830") != -1:
            street_address = " ".join(street_address.split()[:-1])
            city = street_address.split()[-1]
        if adr.find("1830") != -1:
            city = adr.split()[-1]

        store_number = "<MISSING>"
        text = "".join(d.xpath('.//a[contains(text(), "Get Direction")]/@href'))
        try:
            if text.find("ll=") != -1:
                latitude = text.split("ll=")[1].split(",")[0]
                longitude = text.split("ll=")[1].split(",")[1].split("&")[0]
            else:
                latitude = text.split("@")[1].split(",")[0]
                longitude = text.split("@")[1].split(",")[1]
        except IndexError:
            latitude, longitude = "<MISSING>", "<MISSING>"
        hours_of_operation = (
            " ".join(d.xpath('.//a[contains(text(), "Get")]/following-sibling::text()'))
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
