import csv
import json
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

    locator_domain = "https://www.pizzaguys.com"
    api_url = "https://www.pizzaguys.com/locations/"
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
    jsblock = (
        "".join(
            tree.xpath('//script[contains(text(), "var maplistScriptParamsKo")]/text()')
        )
        .split("var maplistScriptParamsKo = ")[1]
        .split("/*")[0]
        .replace("};", "}")
        .strip()
    )
    js = json.loads(jsblock)

    for j in js["KOObject"][0]["locations"]:
        desc = j.get("description")

        d = html.fromstring(desc)
        slug = "".join(d.xpath('//a[./span[text()="Store Info"]]/@href'))
        if slug.find("locations") == -1 and slug.find("location") == -1:
            slug = f"/locations/{slug}"
        numslug = "".join(d.xpath('//a[./span[text()="Order Online"]]/@href'))
        page_url = f"{locator_domain}{slug}"

        latitude = j.get("latitude")
        longitude = j.get("longitude")
        location_name = j.get("title")

        session = SgRequests()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)

        location_type = "Pizza Guys"
        ad = (
            " ".join(tree.xpath('//h2[@class="location-contact-title"]/text()'))
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
        if ad == "<MISSING>":
            ad = (
                " ".join(d.xpath('//p[@class="address"]/text()'))
                .replace("\n", "")
                .strip()
            )
        a = usaddress.tag(ad, tag_mapping=tag)[0]

        street_address = f"{a.get('address1')} {a.get('address2')}".replace(
            "None", ""
        ).strip()
        state = a.get("state") or "<MISSING>"
        postal = a.get("postal") or "<MISSING>"
        country_code = "USA"
        city = a.get("city") or "<MISSING>"
        if city.find("Pablo Townecenter San Pablo") != -1:
            street_address = street_address + " " + "Pablo Townecenter"
            city = "San Pablo"
        try:
            store_number = numslug.split("store=")[1].strip()
        except:
            store_number = "<MISSING>"
        phone = "".join(tree.xpath('//p[@class="call-now"]/a/text()'))
        hours_of_operation = (
            " ".join(
                tree.xpath(
                    '//ul[@class="store-hours-list"]/li[not(contains(@class, "special"))]/span/text()'
                )
            )
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )

        cms = "".join(tree.xpath('//h2[text()="Coming Soon!"]/text()'))
        if cms:
            hours_of_operation = "Coming Soon"

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
