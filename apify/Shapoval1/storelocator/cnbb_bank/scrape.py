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

    locator_domain = "https://www.cnbb.bank"
    api_url = "https://www.cnbb.bank/About-CNB/Locations"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath(
        '//h2[text()="Our Office and ATM Locations"]/following-sibling::p/a'
    )
    for d in div:
        slug = "".join(d.xpath(".//@href"))

        page_url = f"{locator_domain}{slug}"

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
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)

        block = tree.xpath('//h3[./a[@class="LA-ui-accordion-header"]]')
        for b in block:

            location_name = "".join(b.xpath(".//a/text()"))
            ad = b.xpath(
                './/following-sibling::div[1]//h4[text()="Address:"]/following-sibling::p[1]/text()'
            )
            ad = list(filter(None, [a.strip() for a in ad]))
            ad = " ".join(ad).replace("In the Market House Plaza", "").strip()
            a = usaddress.tag(ad, tag_mapping=tag)[0]
            location_type = "Branch"
            street_address = f"{a.get('address1')} {a.get('address2')}".replace(
                "None", ""
            ).strip()
            state = a.get("state") or "<MISSING>"
            postal = a.get("postal") or "<MISSING>"
            country_code = "US"
            city = a.get("city").replace("Second Floor", "").strip() or "<MISSING>"
            store_number = "<MISSING>"
            latitude = "<MISSING>"
            longitude = "<MISSING>"
            phone = b.xpath(
                './/following-sibling::div[1]//h4[text()="Phone:"]/following-sibling::p[1]/text()'
            )
            phone = list(filter(None, [a.strip() for a in phone]))
            phone = " ".join(phone).replace("Phone:", "").strip()
            if phone.find("or") != -1:
                phone = phone.split("or")[0].strip()

            hours_of_operation = b.xpath(
                './/following-sibling::div[1]//h4[contains(text(), "Hours")]/following-sibling::p[1]//text()'
            )
            hours_of_operation = list(
                filter(None, [a.strip() for a in hours_of_operation])
            )
            hours_of_operation = " ".join(hours_of_operation) or "<MISSING>"

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
