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
    locator_domain = "https://mezeh.com"
    page_url = "https://mezeh.com/locations/"

    cookies = {
        "visid_incap_2515619": "/J/3KrpARHyb1/hxT/2tIpJmaGAAAAAAQUIPAAAAAAAU+YXsXdDFPyV0odDvd6fx",
        "incap_ses_1344_2515619": "fkxYcPO4byiUdNguBNmmEsgZamAAAAAARXCq/1CxURJnxhMUj5pqnw==",
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Connection": "keep-alive",
        "Referer": "https://mezeh.com/",
        "Upgrade-Insecure-Requests": "0",
        "TE": "Trailers",
    }
    session = SgRequests()
    r = session.get(page_url, headers=headers, cookies=cookies)
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
    div = tree.xpath(
        '//div[@class="column_attr clearfix align_left mobile_align_left"]'
    )
    for j in div:
        coming_soon = "".join(j.xpath(".//h3/strong/text()"))
        if coming_soon.find("coming soon") != -1:
            continue

        ad = j.xpath(".//h5/text()")
        ad = list(filter(None, [a.strip() for a in ad]))
        line = " ".join(ad[:2])
        a = usaddress.tag(line, tag_mapping=tag)[0]
        street_address = f"{a.get('address1')} {a.get('address2')}".replace(
            "None", ""
        ).strip()
        city = a.get("city")
        postal = a.get("postal")
        state = a.get("state")
        phone = (
            "".join(
                j.xpath(
                    './/strong[contains(text(), "hours")]/preceding-sibling::text()[2]'
                )
            )
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
        hours_of_operation = j.xpath(
            './/strong[contains(text(), "hours")]/following-sibling::text()'
        )
        hours_of_operation = list(filter(None, [a.strip() for a in hours_of_operation]))
        hours_of_operation = " ".join(hours_of_operation) or "<MISSING>"
        country_code = "US"
        store_number = "<MISSING>"
        page_url = "https://mezeh.com/locations/"
        location_name = " ".join(j.xpath(".//h4/text()")).strip()
        if location_name.find("temporarily closed") != -1:
            location_name = location_name.split("temporarily closed")[0].strip()
        if location_name.find("spring forest") != -1:
            hours_of_operation = "Temporarily closed"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        location_type = "<MISSING>"

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
