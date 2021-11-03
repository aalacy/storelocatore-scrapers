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

    locator_domain = "https://www.unibankusa.com"
    page_url = "https://www.unibankusa.com/en-us/About-Us/Contact-Us"
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
        '//h2[./span[contains(text(), "Branch")]] | //h2[./span[contains(text(), "Loan")]]'
    )
    for d in div:

        ad = " ".join(
            d.xpath(
                './/following-sibling::p[1]/strong[contains(text(), "Address")]/following-sibling::text()[1] | .//following-sibling::p[1]/strong[contains(text(), "Address")]/following-sibling::span/text()'
            )
        ).strip()
        a = usaddress.tag(ad, tag_mapping=tag)[0]
        location_name = "".join(d.xpath(".//span/text()")).strip()
        location_type = "<MISSING>"
        if location_name.find("Branch") != -1:
            location_type = "Branch"
        if location_name.find("Loan") != -1:
            location_type = "Loan Office"
        street_address = f"{a.get('address1')} {a.get('address2')}".replace(
            "None", ""
        ).strip()

        state = a.get("state") or "<MISSING>"
        postal = a.get("postal") or "<MISSING>"
        if street_address.find("671") != -1:
            postal = "29909"

        country_code = "US"
        city = a.get("city") or "<MISSING>"
        store_number = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        phone = " ".join(
            d.xpath(
                './/following-sibling::p[1]/strong[contains(text(), "Phone Number:")]/following-sibling::text()[1]'
            )
        ).strip()
        hours_of_operation = "<MISSING>"
        if location_type == "Branch":
            hours_of_operation = (
                " ".join(
                    d.xpath(
                        './/following-sibling::h2[./span[text()="BUSINESS HOURS"]]/following-sibling::p[2]//text()'
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
