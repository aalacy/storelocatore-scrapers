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
    r = session.get("https://movatiathletic.com/slider/locations.php")
    tree = html.fromstring(r.text)

    return tree.xpath("//ul/li/a/@href")


def get_coords_from_google_url(url):
    try:
        if url.find("ll=") != -1:
            latitude = url.split("ll=")[1].split(",")[0]
            longitude = url.split("ll=")[1].split(",")[1].split("&")[0]
        else:
            latitude = url.split("@")[1].split(",")[0]
            longitude = url.split("@")[1].split(",")[1]
    except IndexError:
        latitude, longitude = "<MISSING>", "<MISSING>"

    return latitude, longitude


def get_data(url):
    locator_domain = "https://movatiathletic.com/"
    page_url = f"https://movatiathletic.com{url}"

    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    location_name = "".join(
        tree.xpath("//div[@class='clubAddress']/div[not(@class)]/text()")
    ).strip()
    line = tree.xpath("//div[@class='clubAddressInfo']/text()")
    line = list(filter(None, [l.strip() for l in line]))
    if not line:
        return

    street_address = ", ".join(line[:-1])
    line = line[-1]
    city = line.split(",")[0].strip()
    line = line.split(",")[1].strip()
    state = line.split()[0]
    postal = line.replace(state, "").strip()
    country_code = "CA"
    store_number = "<MISSING>"
    phone = (
        "".join(tree.xpath("//div[@class='clubAddressInfo']/a/text()")).strip()
        or "<MISSING>"
    )
    text = "".join(tree.xpath("//a[contains(@href, 'google')]/@href"))
    latitude, longitude = get_coords_from_google_url(text)
    location_type = "<MISSING>"

    _tmp = []
    hours = tree.xpath("//div[@class='hoursrow highlight-row']/following-sibling::div")
    for h in hours:
        day = "".join(h.xpath("./div[1]/text()")).split(",")[0].strip()
        time = "".join(h.xpath("./div[2]/span/text()")).strip()
        _tmp.append(f"{day}: {time}")

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
