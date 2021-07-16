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

    locator_domain = "https://www.nexusdistribution.com"
    page_url = "https://www.nexusdistribution.com/locations"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    jsblock = "".join(
        tree.xpath(
            '//div[@class="sqs-block map-block sqs-block-map sized vsize-12"]/@data-block-json'
        )
    )
    js = json.loads(jsblock)
    location_name = "".join(tree.xpath("//h2/text()"))
    location_type = "<MISSING>"
    street_address = js.get("location").get("addressLine1")
    ad = "".join(js.get("location").get("addressLine2"))
    state = ad.split(",")[1].strip()
    postal = ad.split(",")[2].strip()
    country_code = js.get("location").get("addressCountry")
    city = ad.split(",")[0].strip()
    store_number = "<MISSING>"
    latitude = js.get("location").get("mapLat")
    longitude = js.get("location").get("mapLng")

    session = SgRequests()
    r = session.get("https://www.nexusdistribution.com/contact", headers=headers)
    tree = html.fromstring(r.text)

    phone = "".join(tree.xpath("//h1/following-sibling::p[2]/text()[1]"))
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
