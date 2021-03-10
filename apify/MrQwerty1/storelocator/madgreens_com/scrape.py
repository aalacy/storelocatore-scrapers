import csv
import re

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
    r = session.get("https://www.madgreens.com/locations")
    tree = html.fromstring(r.text)

    return tree.xpath("//a[text()='View Full Details']/@href")


def get_data(url):
    locator_domain = "https://www.madgreens.com/"
    page_url = f"https://www.madgreens.com{url}"

    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    location_name = "".join(
        tree.xpath("//div[@class='title-wrapper']/h2/text()")
    ).strip()
    street_address = (
        " ".join(" ".join(tree.xpath("//div[@class='street-block']//text()")).split())
        or "<MISSING>"
    )
    city = (
        "".join(tree.xpath("//span[@class='locality']/text()")).strip() or "<MISSING>"
    )
    state = "".join(tree.xpath("//span[@class='state']/text()")).strip() or "<MISSING>"
    postal = (
        "".join(tree.xpath("//span[@class='postal-code']/text()")).strip()
        or "<MISSING>"
    )
    country_code = "US"
    store_number = "<MISSING>"
    phone = (
        "".join(tree.xpath("//div[@property='schema:servicePhone']/text()")).strip()
        or "<MISSING>"
    )

    text = "".join(tree.xpath("//script[contains(text(), 'jQuery.extend')]/text()"))
    latitude = "".join(re.findall(r'"latitude":(\d+.\d+)', text)) or "<MISSING>"
    longitude = "".join(re.findall(r'"longitude":(-?\d+.\d+)', text)) or "<MISSING>"
    location_type = "<MISSING>"

    _tmp = []
    span = tree.xpath("//span[@class='oh-display']")

    for s in span:
        day = "".join(s.xpath("./span/text()")).strip()
        time = "".join(s.xpath("./div/text()")).strip()
        _tmp.append(f"{day} {time}")

    hours_of_operation = ";".join(_tmp) or "<MISSING>"

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

    return row


def fetch_data():
    out = []
    urls = get_urls()

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_data, url): url for url in urls}
        for future in futures.as_completed(future_to_url):
            row = future.result()
            if row:
                out.append(row)

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
