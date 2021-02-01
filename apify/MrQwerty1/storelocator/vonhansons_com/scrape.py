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
    r = session.get("https://vonhansons.com/")
    tree = html.fromstring(r.text)

    return tree.xpath(
        "//ul[@class='ubermenu-submenu ubermenu-submenu-id-1428 ubermenu-submenu-type-auto ubermenu-submenu-type-mega ubermenu-submenu-drop ubermenu-submenu-align-full_width']//a[contains(@href, '.com')]/@href"
    )


def get_data(page_url):
    locator_domain = "https://vonhansons.com/"

    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    location_name = "".join(tree.xpath("//h1/text()")).replace("Welcome to", "").strip()
    line = tree.xpath("//div[@class='one-half first']/p[1]/text()")
    if not line:
        line = tree.xpath("//div[@class='one-half first']/p[2]/text()")
        if not line:
            line = tree.xpath("//div[@class='one-half first']/text()")

    line = list(filter(None, [l.strip() for l in line]))

    if line[-1].find(",") != -1:
        street_address = ", ".join(line[:-1])
        line = line[-1]
        city = line.split(",")[0].strip()
        line = line.split(",")[1].strip()
    else:
        line = line[0]
        street_address = line.split(",")[0]
        city = line.split(",")[1].strip()
        line = line.split(",")[-1].strip()

    state = line.split()[0]
    postal = line.split()[1]
    country_code = "US"
    store_number = "<MISSING>"
    try:
        phone = (
            tree.xpath(
                "//p[.//*[contains(text(), 'Tel')] or contains(text(), 'Tel')]/text()"
            )[0]
            .replace("Tel:", "")
            .strip()
        )
    except IndexError:
        phone = "<MISSING>"
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    location_type = "<MISSING>"

    hours = tree.xpath(
        "//p[./strong[contains(text(), 'Hours')]]/text()|//p[./strong[contains(text(), 'Hours')]]/following-sibling::p/text()"
    )
    hours = list(filter(None, [h.strip() for h in hours]))
    hours_of_operation = ";".join(hours) or "<MISSING>"

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
