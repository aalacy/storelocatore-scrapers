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


def get_cities():
    session = SgRequests()
    r = session.get("https://www.wework.com/locations")
    tree = html.fromstring(r.text)

    return tree.xpath(
        "//ul[contains(@class,'list--US') or contains(@class, 'list--CA')]//a/@href"
    )


def get_urls(url):
    session = SgRequests()
    r = session.get(f"https://www.wework.com{url}")
    tree = html.fromstring(r.text)

    return tree.xpath("//a[@class='ray-card ray-card--link building-card']/@href")


def get_data(url):
    locator_domain = "https://www.wework.com/"
    page_url = f"https://www.wework.com{url}"

    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    location_name = "".join(tree.xpath("//h1/span/text()")).strip()
    line = "".join(tree.xpath("//address[@class='building-address']/text()")).split(
        "\n"
    )
    line = list(filter(None, [l.strip() for l in line]))

    street_address = ", ".join(line[:-1])
    line = line[-1]
    city = line.split(",")[0].strip()
    line = line.split(",")[1].strip()
    state = line.split()[0]
    postal = line.replace(state, "").replace("AB ", "").strip() or "<MISSING>"
    country_code = "US"
    if len(postal) != 5:
        country_code = "CA"
    store_number = "<MISSING>"
    try:
        phone = tree.xpath(
            "//div[@class='lead-form-contact-footer__inner']//a[contains(@href, 'tel:')]/text()"
        )[0].strip()
    except IndexError:
        phone = "<MISSING>"

    try:
        text = "".join(tree.xpath("//script[contains(text(), 'latitude')]/text()"))
        latitude = text.split('"latitude":"')[1].split('"')[0]
        longitude = text.split('"longitude":"')[1].split('"')[0]
    except IndexError:
        latitude, longitude = "<MISSING>", "<MISSING>"
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

    return row


def fetch_data():
    out = []
    urls = []
    cities = get_cities()

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_urls, url): url for url in cities}
        for future in futures.as_completed(future_to_url):
            urls += future.result()

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
