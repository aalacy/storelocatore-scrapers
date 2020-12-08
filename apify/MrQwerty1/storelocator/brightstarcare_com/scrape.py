import csv
import json

from concurrent import futures
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


def get_urls():
    session = SgRequests()
    r = session.get("https://www.brightstarcare.com/about-us/find-a-location")
    tree = html.fromstring(r.content)

    return tree.xpath("//section[@class='map-list']//div[@class='row']//a/@href")


def get_data(url):
    rows = []
    locator_domain = "https://www.brightstarcare.com/"

    session = SgRequests()
    r = session.get(f"https://www.brightstarcare.com{url}")
    tree = html.fromstring(r.text)
    items = tree.xpath(
        "//section[@class='map-list content-list-container']//div[@class='row']"
    )

    for item in items:
        text = (
            "".join(item.xpath(".//script/text()"))
            .replace("locations.push(", "")
            .replace(");", "")
            .strip()
        )
        a = json.loads(text)
        location_name = "".join(item.xpath(".//h3/text()")).strip() or "<MISSING>"
        page_url = f'https://www.brightstarcare.com{a.get("url")}'
        street_address = a.get("address") or "<MISSING>"
        city = a.get("city") or "<MISSING>"
        state = a.get("state") or "<MISSING>"
        postal = "".join(a.get("zipcode").split()) or "<MISSING>"
        country_code = "US"
        store_number = "<MISSING>"
        phone = (
            "".join(item.xpath(".//span[@class='js-phone']/text()")).strip()
            or "<MISSING>"
        )
        latitude = a.get("lat") or "<MISSING>"
        longitude = a.get("lng") or "<MISSING>"

        location_type = "<MISSING>"
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

        rows.append(row)

    return rows


def fetch_data():
    out = []
    urls = get_urls()

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_data, url): url for url in urls}
        for future in futures.as_completed(future_to_url):
            rows = future.result()
            for row in rows:
                out.append(row)

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
