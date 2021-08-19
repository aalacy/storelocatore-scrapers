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

    locator_domain = "https://prettykittywax.com/"
    api_url = "https://prettykittywax.com/"
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
    div = tree.xpath('//a[@style="color: #2d2d2d;"]')
    for d in div:

        page_url = "".join(d.xpath(".//@href"))
        if (
            page_url
            == "https://prettykittywax.wpengine.com/locations/tx/houston-wash-heights/"
        ):
            continue
        if (
            page_url
            == "https://prettykittywax.wpengine.com/locations/tx/dallas-uptown/"
        ):
            continue
        if (
            page_url
            == "https://prettykittywax.wpengine.com/locations/tx/dallas-mockingbird/"
        ):
            continue
        if (
            page_url
            == "https://prettykittywax.wpengine.com/locations/tx/dallas-southlake/"
        ):
            page_url = "https://prettykittywax.com/locations/tx/dallas-south-lake/"
        session = SgRequests()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)
        ad = tree.xpath(
            '//div[@class="elementor-section-wrap"]/section[4]/div/div/div[1]//h2/text()'
        )
        ad = list(filter(None, [a.strip() for a in ad]))
        if "closed permanently" in "".join(ad):
            continue
        ad = " ".join(ad).replace("\n", " ").replace(",", "").strip()
        a = usaddress.tag(ad, tag_mapping=tag)[0]
        location_name = tree.xpath('//h2[contains(text(), "The Pretty Kitty")]/text()')
        location_name = "".join(location_name[0]).strip()

        location_type = "Location"
        street_address = f"{a.get('address1')} {a.get('address2')}".replace(
            "None", ""
        ).strip()
        state = a.get("state") or "<MISSING>"
        postal = a.get("postal") or "<MISSING>"
        country_code = "USA"
        city = a.get("city") or "<MISSING>"
        store_number = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        phone = "".join(
            tree.xpath(
                '//div[@class="elementor-section-wrap"]/section[4]/div/div/div[2]//a/text()'
            )
        ).strip()
        hours_of_operation = (
            " ".join(
                tree.xpath(
                    '//div[@class="elementor-section-wrap"]/section[4]/div/div/div[3]//h2/text()'
                )
            )
            .replace("\n", "")
            .replace("   ", "  ")
            .strip()
        )
        if hours_of_operation.find("Modified Hours") != -1:
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
