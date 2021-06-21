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

    locator_domain = "https://www.daymarkrecovery.org"
    api_url = "https://www.daymarkrecovery.org/locations"

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
    jsblock = "".join(tree.xpath('//script[contains(text(), "markers")]/text()'))
    js = json.loads(jsblock)

    for j in js["markers"]:

        content = j.get("content")
        a = html.fromstring(content)
        slug = "".join(a.xpath("//a/@href"))

        page_url = f"{locator_domain}{slug}"
        phone = (
            "".join(a.xpath('//div[contains(text(), "Phone:")]/text()'))
            .replace("\n", "")
            .replace("Phone:", " ")
            .strip()
        )
        if phone.find(" ") != -1:
            phone = phone.split()[-1].strip()
        location_name = "".join(a.xpath("//h3/text()")).replace("\n", "").strip()
        latitude = j.get("lat")
        longitude = j.get("lng")
        if page_url == "https://www.daymarkrecovery.org/locations/fbc-iredell":
            page_url = "https://www.daymarkrecovery.org/locations"
        if page_url == "https://www.daymarkrecovery.org/locations/psr-chatham":
            page_url = "https://www.daymarkrecovery.org/locations"
        if page_url == "https://www.daymarkrecovery.org/locations/psr-person":
            page_url = "https://www.daymarkrecovery.org/locations"

        session = SgRequests()
        r = session.get(page_url, headers=headers)

        tree = html.fromstring(r.text)

        location_type = "Daymark Recovery Services"

        ad = (
            " ".join(
                tree.xpath('//h3[text()="Contact"]/following-sibling::h4[1]/text()')
            )
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )
        if ad == "<MISSING>":
            ad = (
                " ".join(
                    tree.xpath(
                        f'//h3[./a[text()="{location_name}"]]/following-sibling::div/text()[position()<3]'
                    )
                )
                .replace("\n", "")
                .strip()
            )
        a = usaddress.tag(ad, tag_mapping=tag)[0]
        street_address = f"{a.get('address1')} {a.get('address2')}".replace(
            "None", ""
        ).strip()
        state = a.get("state") or "<MISSING>"
        postal = a.get("postal") or "<MISSING>"
        country_code = "US"
        city = a.get("city") or "<MISSING>"
        store_number = "<MISSING>"
        hours_of_operation = (
            tree.xpath(
                '//h3[text()="Contact"]/following-sibling::p[./strong[contains(text(), "Hours")]][1]/strong/following-sibling::text()'
            )
            or "<MISSING>"
        )
        if hours_of_operation != "<MISSING>":
            hours_of_operation = list(
                filter(None, [a.strip() for a in hours_of_operation])
            )
            hours_of_operation = " ".join(hours_of_operation).replace(":", "").strip()
        hours_of_operation = (
            hours_of_operation.replace("Outpatient", "")
            .replace("BHUC Unit 24/7", "")
            .replace("After 5PM by Appt Only", "")
            .replace("  ", " ")
            .strip()
        )
        if hours_of_operation == "24/7":
            hours_of_operation = "<MISSING>"
        hours_of_operation = (
            hours_of_operation.replace("24/7", "").replace("730PM", "7:30PM").strip()
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
