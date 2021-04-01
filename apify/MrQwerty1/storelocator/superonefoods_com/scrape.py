import csv

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
    r = session.get("https://www.superonefoods.com/store-finder")
    tree = html.fromstring(r.text)

    return tree.xpath("//a[@class='store-name']/@href")


def get_data(url):
    locator_domain = "https://www.superonefoods.com/"
    page_url = f"https://www.superonefoods.com{url}"

    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    h1 = tree.xpath("//h1/text()")
    if len(h1) == 2:
        d = tree.xpath("//div[@class='col-sm-12 col-md-6']")[0]
    else:
        d = tree.xpath("//div[@class='col-sm-12 col-md-4 col-md-pull-8']")[0]
    location_name = tree.xpath("//h1/text()")[0].strip()
    line = d.xpath(".//address/text()")
    line = list(filter(None, [l.strip() for l in line]))
    street_address = " ".join(line[:-1])
    line = line[-1]
    city = line.split(",")[0].strip()
    line = line.split(",")[1].strip()
    state = line.split()[0]
    postal = line.split()[1]
    country_code = "US"
    store_number = "<MISSING>"
    phone = (
        "".join(d.xpath(".//a[contains(@href, 'tel')]/text()")).strip() or "<MISSING>"
    )
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    location_type = "<MISSING>"
    hours_of_operation = (
        d.xpath(".//div[@class='store-hours']//li/text()")[0]
        .replace("Store:", "")
        .strip()
        or "<MISSING>"
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

    return row


def fetch_data():
    out = []
    urls = get_urls()

    with futures.ThreadPoolExecutor(max_workers=5) as executor:
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
