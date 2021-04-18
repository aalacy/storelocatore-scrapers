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

    locator_domain = "https://www.snapcustompizza.com"
    api_url = "https://www.snapcustompizza.com/locations-and-menus/"
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
    div = tree.xpath('//a[@class="card__btn"]')
    for d in div:
        slug = "".join(d.xpath(".//@href"))
        page_url = f"{locator_domain}{slug}"
        session = SgRequests()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)

        location_name = (
            "".join(
                tree.xpath(
                    '//h1[contains(text(), "Hours")]/following-sibling::p[1]/a[1]/text()[1]'
                )
            )
            .replace("\n", "")
            .replace(",", "")
            .strip()
        )

        ad = (
            " ".join(
                tree.xpath(
                    '//h1[contains(text(), "Hours")]/following-sibling::p[1]/a[1]/text()[2]'
                )
            )
            .replace("\n", "")
            .replace(",", "")
            .replace("ShopRite - ", "")
            .strip()
        )
        a = usaddress.tag(ad, tag_mapping=tag)[0]

        location_type = "<MISSING>"
        phone = "".join(tree.xpath('//a[contains(@href, "tel")]/text()'))
        street_address = f"{a.get('address1')} {a.get('address2')}".replace(
            "None", ""
        ).strip()
        state = a.get("state") or "<MISSING>"
        postal = a.get("postal") or "<MISSING>"
        country_code = "US"
        city = a.get("city") or "<MISSING>"
        if city == "<MISSING>":
            city = location_name.capitalize()
        store_number = "<MISSING>"
        latitude = "".join(tree.xpath('//div[@class="gmaps"]/@data-gmaps-lat'))
        longitude = "".join(tree.xpath('//div[@class="gmaps"]/@data-gmaps-lng'))
        hours_of_operation = (
            " ".join(tree.xpath('//div[@class="col-md-6"]/p[./strong]//text()'))
            .replace("\n", "")
            .strip()
            or "Temporarily Closed"
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
