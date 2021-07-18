import csv
import json
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

    locator_domain = "https://tadsrestaurants.com"
    page_url = "https://tadsrestaurants.com/visit-tremont"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[@class="col sqs-col-3 span-3"]')
    for d in div:

        location_name = "".join(d.xpath(".//h2/text()"))
        location_type = "<MISSING>"
        ll = "".join(d.xpath(".//div/@data-block-json"))
        js = json.loads(ll)
        street_address = js.get("location").get("addressLine1")

        state = (
            "".join(d.xpath('.//div[@class="sqs-block-content"]/h3[3]/text()'))
            .split(",")[1]
            .strip()
        )
        postal = "".join(js.get("location").get("addressLine2")).split()[-1].strip()

        country_code = "USA"
        city = (
            "".join(d.xpath('.//div[@class="sqs-block-content"]/h3[3]/text()'))
            .split(",")[0]
            .strip()
        )
        store_number = "<MISSING>"

        latitude = js.get("location").get("mapLat")
        longitude = js.get("location").get("mapLng")
        phone = "".join(d.xpath(".//p/text()"))

        hours_of_operation = (
            "".join(d.xpath('.//following::p[contains(text(), "We open at")]/text()'))
            .replace("We open at", "")
            .strip()
        )
        close = (
            "".join(d.xpath('.//following::p[contains(text(), "KITCHENS")]/text()'))
            .replace("KITCHENS AT ALL LOCATIONS CLOSE AT", "")
            .strip()
        )
        hours_of_operation = hours_of_operation.replace("am", f"am to {close}")

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
