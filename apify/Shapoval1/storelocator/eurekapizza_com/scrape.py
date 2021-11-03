import csv
from lxml import html
import usaddress
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
    locator_domain = "https://www.eurekapizza.com"
    api_url = "https://www.eurekapizza.com/order-now"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Upgrade-Insecure-Requests": "1",
        "Connection": "keep-alive",
    }
    r = session.get(api_url, headers=headers)
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
    block = tree.xpath('//li[@class="photoGalleryThumbs"]')
    for j in block:

        ad = " ".join(j.xpath('.//p[@class="rteBlock"]//text()'))
        if ad.find("(") != -1:
            ad = ad.split("(")[0].strip()
        if ad.find("Featuring") != -1:
            ad = ad.split("Featuring")[0].strip()

        a = usaddress.tag(ad, tag_mapping=tag)[0]
        street_address = (
            f"{a.get('address1')} {a.get('address2')}".replace("None", "").strip()
            or "<MISSING>"
        )
        city = a.get("city") or "<MISSING>"
        state = a.get("state") or "<MISSING>"
        postal = a.get("postal") or "<MISSING>"
        if street_address.find("Zero") != -1:
            street_address = "2900 Zero St"
            city = "Fort Smith"
        country_code = "US"
        store_number = "<MISSING>"
        slug = "".join(j.xpath('.//div[@class="image-container"]/a/@href'))
        location_name = "".join(
            j.xpath('.//h3[contains(@class, "caption-title")]/text()')
        )

        page_url = f"https://www.eurekapizza.com{slug}"
        if page_url.find("adorapos") != -1:
            page_url = slug
        session = SgRequests()
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
            "Upgrade-Insecure-Requests": "1",
            "Connection": "keep-alive",
        }
        r = session.get(page_url, headers=headers)
        trees = html.fromstring(r.text)

        phone = (
            "".join(
                trees.xpath(
                    "//div[contains(@class, 'dmNewParagraph ')]/text() | //span[@class='lh-1 size-16']/div[contains(text(), '-')]/text() | //div[@class='u_1031901913 dmNewParagraph']/text()"
                )
            )
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
        latitude = (
            "".join(trees.xpath("//div[contains(@class, " "inlineMap)]/@data-lat"))
            or "<MISSING>"
        )
        longitude = (
            "".join(trees.xpath("//div[contains(@class, " "inlineMap)]/@data-lng"))
            or "<MISSING>"
        )
        location_type = "<MISSING>"

        hours_of_operation = "<MISSING>"

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
