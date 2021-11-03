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

    locator_domain = "https://www.burgermonger.com"
    page_url = "https://www.burgermonger.com/locations"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath("//section[position()>1]")

    for d in div:

        location_name = "".join(d.xpath('.//h2[@class="location"]/text()'))
        location_type = "Restaurant"
        street_address = "".join(
            d.xpath('.//div[@class="sqs-block-content"]/p[1]/text()[1]')
        )
        ad = (
            "".join(d.xpath('.//div[@class="sqs-block-content"]/p[1]/text()[2]'))
            .replace("\n", "")
            .strip()
        )
        phone = (
            "".join(d.xpath('.//div[@class="sqs-block-content"]/p[1]/text()[3]'))
            .replace("\n", "")
            .strip()
        )
        state = ad.split(",")[1].split()[0].strip()
        postal = ad.split(",")[1].split()[1].strip()
        city = ad.split(",")[0].strip()
        country_code = "US"
        store_number = "<MISSING>"
        ll = "".join(
            d.xpath(
                './/div[@class="sqs-block map-block sqs-block-map"]/@data-block-json'
            )
        )
        js = json.loads(ll)
        latitude = js.get("location").get("markerLat")
        longitude = js.get("location").get("markerLng")
        hours_of_operation = (
            " ".join(d.xpath('.//div[@class="sqs-block-content"]/p[2]/text()'))
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
