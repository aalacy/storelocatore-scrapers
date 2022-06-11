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

    locator_domain = "https://midwestexpressclinic.com"
    api_url = "https://midwestexpressclinic.com/locations/"

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
    div = (
        "".join(tree.xpath("//script[contains(text(), 'var map1 = ')]/text()"))
        .split('"places":')[1]
        .split(',"styles"')[0]
    )
    js = json.loads(div)
    for j in js:
        m = j.get("location")
        ad = "".join(j.get("address")).replace("\n", " ").replace("<br>", " ").strip()
        a = usaddress.tag(ad, tag_mapping=tag)[0]
        page_url = f"https://midwestexpressclinic.com/locations/{m.get('extra_fields').get('Slug')}"
        street_address = f"{a.get('address1')} {a.get('address2')}".replace(
            "None", ""
        ).strip()
        city = a.get("city")
        if ad.find("7343") != -1:
            street_address = " ".join(ad.split(",")[0].split()[:3]).strip()
            city = " ".join(ad.split(",")[0].split()[3:]).strip()

        state = a.get("state")
        postal = a.get("postal")
        store_number = "<MISSING>"
        location_name = j.get("title")
        latitude = m.get("lat")
        longitude = m.get("lng")
        country_code = "US"
        location_type = "<MISSING>"
        phone = m.get("extra_fields").get("Phone Number")
        session = SgRequests()
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
        }
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)
        hours_of_operation = tree.xpath(
            '//div[@class="et_pb_column et_pb_column_1_2 et_pb_column_2  et_pb_css_mix_blend_mode_passthrough"]/div[4]//text()'
        )
        hours_of_operation = list(filter(None, [a.strip() for a in hours_of_operation]))
        hours_of_operation = (
            "".join(hours_of_operation).replace("\ue60d", "").strip() or "<MISSING>"
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
