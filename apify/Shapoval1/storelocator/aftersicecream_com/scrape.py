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

    locator_domain = "https://www.aftersicecream.com"
    page_url = "https://www.aftersicecream.com/locations"
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

    div = tree.xpath('//div[contains(@class, "sqs-col-5 span-5")]')
    for d in div:
        location_name = " ".join(
            d.xpath(
                './/following-sibling::div[1][@class="sqs-block html-block sqs-block-html"]/div/h3[1]//text() | .//preceding-sibling::div[@class="col sqs-col-7 span-7"]/div//h3//text()'
            )
        )
        location_name = location_name.lower().capitalize().replace(" beac h", " beach")
        if location_name.find("*") != -1:
            location_name = location_name.split("*")[0].strip()
        location_type = "<MISSING>"
        adr = " ".join(d.xpath(".//p//text()")).replace("\n", "").strip()
        a = usaddress.tag(adr, tag_mapping=tag)[0]
        street_address = f"{a.get('address1')} {a.get('address2')}".replace(
            "None", ""
        ).strip()
        phone = "<MISSING>"
        state = "".join(a.get("state")).upper() or "<MISSING>"
        postal = "".join(a.get("postal")).replace(" ", "").strip() or "<MISSING>"
        country_code = "US"
        city = "".join(a.get("city")).capitalize() or "<MISSING>"
        store_number = "<MISSING>"
        text = (
            " ".join(
                d.xpath(
                    './/following-sibling::div[1][@class="sqs-block html-block sqs-block-html"]/div/h3//a/@href | .//preceding-sibling::div[@class="col sqs-col-7 span-7"]/div//h3//a/@href'
                )
            )
            or "<MISSING>"
        )
        try:
            if text.find("ll=") != -1:
                latitude = text.split("ll=")[1].split(",")[0]
                longitude = text.split("ll=")[1].split(",")[1].split("&")[0]
            else:
                latitude = text.split("@")[1].split(",")[0]
                longitude = text.split("@")[1].split(",")[1]
        except IndexError:
            latitude, longitude = "<MISSING>", "<MISSING>"
        hours_of_operation = "".join(
            d.xpath(".//preceding::h2[contains(text(), 'errr')]/text()")
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
