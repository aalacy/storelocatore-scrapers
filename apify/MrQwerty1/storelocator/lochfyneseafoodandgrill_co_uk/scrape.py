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
    r = session.get("https://www.lochfyneseafoodandgrill.co.uk/locations")
    tree = html.fromstring(r.text)

    return tree.xpath("//a[contains(@href, '/locations/')]/@href")


def get_data(url):
    locator_domain = "https://www.lochfyneseafoodandgrill.co.uk/"
    page_url = f"https://www.lochfyneseafoodandgrill.co.uk{url}"

    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    location_name = "".join(tree.xpath("//h1[@id='page-title']/text()")).strip()
    street_address = (
        "".join(tree.xpath("//div[@class='thoroughfare']/text()")).strip()
        or "<MISSING>"
    )
    city = "".join(tree.xpath("//div[@class='locality']/text()")).strip() or "<MISSING>"
    state = "<MISSING>"
    postal = (
        "".join(tree.xpath("//div[@class='postal-code']/text()")).strip() or "<MISSING>"
    )
    country_code = "GB"
    store_number = "<MISSING>"
    phone = (
        "".join(tree.xpath("//div[@class='location__telephone']/text()")).strip()
        or "<MISSING>"
    )

    try:
        latitude = re.findall(r'"latitude":"(\d+.\d+)"', r.text)[0]
        longitude = re.findall(r'"longitude":"(-?\d+.\d+)"', r.text)[0]
    except IndexError:
        latitude = "<MISSING>"
        longitude = "<MISSING>"
    location_type = "<MISSING>"
    hours = " ".join(
        "".join(tree.xpath("//span[@class='oh-display']//text()")).split()
    ).replace("00 ", "00;")
    if not hours:
        _tmp = []
        hh = tree.xpath("//div[@id='openinghours']/p")
        for h in hh:
            day = "".join(h.xpath("./strong/text()")).strip()
            time = "".join(h.xpath("./text()")).strip()
            _tmp.append(f"{day}: {time}")

        hours = ";".join(_tmp)

    hours_of_operation = hours or "<MISSING>"

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
