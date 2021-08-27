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
    r = session.get("https://saltandstraw.com/pages/locations")
    tree = html.fromstring(r.text)

    return set(tree.xpath("//a[contains(text(), 'LEARN MORE')]/@href"))


def get_data(url):
    locator_domain = "https://saltandstraw.com/"
    if url.startswith("/"):
        page_url = f"https://saltandstraw.com{url}"
    else:
        page_url = url

    r = session.get(page_url)
    tree = html.fromstring(r.text)

    location_name = "".join(tree.xpath("//h1/text()")).strip()
    line = []
    lines = tree.xpath(
        "//div[@class='shg-rich-text shg-theme-text-content' and count(./p)>=2]//text()"
    )
    for l in lines:
        if not l.strip() or ":" in l:
            continue
        line.append(l.strip())
    line = list(filter(None, [l.strip() for l in line]))

    street_address = ", ".join(line[:-1])
    line = line[-1]
    city = line.split(",")[0].strip()
    line = line.split(",")[1].strip()
    state = line.split()[0]
    try:
        postal = line.split()[1]
    except IndexError:
        postal = "<MISSING>"
    country_code = "US"
    store_number = "<MISSING>"
    phone = (
        "".join(
            tree.xpath(
                "//a[contains(@href, 'tel:') or contains(@href, '(')]//text()|//p[.//span[contains(@aria-label, 'Phone')]]//text()"
            )
        ).strip()
        or "<MISSING>"
    )
    latitude = (
        "".join(tree.xpath("//div[@data-latitude]/@data-latitude")) or "<MISSING>"
    )
    longitude = (
        "".join(tree.xpath("//div[@data-longitude]/@data-longitude")) or "<MISSING>"
    )
    location_type = "<MISSING>"
    hours_of_operation = (
        "".join(
            tree.xpath(
                "//div[./div/div[@class='shg-fa shg-fa-clock-o shogun-icon']]/following-sibling::div//text()"
            )
        )
        .strip()
        .replace("\n", ";")
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
    session = SgRequests()
    scrape()
