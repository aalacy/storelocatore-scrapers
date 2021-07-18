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
    r = session.get("https://www.mollymoon.com/locations")
    tree = html.fromstring(r.text)

    return tree.xpath("//div[@class='definition-list footer__locations']//a/@href")


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
    locator_domain = "https://www.mollymoon.com/"
    page_url = f"https://www.mollymoon.com{url}"

    r = session.get(page_url)
    tree = html.fromstring(r.text)

    location_name = "".join(
        tree.xpath("//a[@class='active section-navigation__item']/text()")
    ).strip()
    line = tree.xpath("//div[@class='location-contact']/text()")
    line = list(filter(None, [l.strip() for l in line]))

    street_address = ", ".join(line[:-1])
    line = line[-1].split()
    postal = line.pop()
    state = line.pop()
    city = " ".join(line)
    country_code = "US"
    store_number = "<MISSING>"
    phone = (
        "".join(tree.xpath("//div[@class='location-contact']/span/text()")).strip()
        or "<MISSING>"
    )
    text = "".join(tree.xpath("//script[contains(text(), 'var mmLink')]/text()"))
    latitude, longitude = get_coords_from_google_url(text)
    location_type = "<MISSING>"
    hours_of_operation = (
        "".join(tree.xpath("//div[@class='location-contact']/h2/text()"))
        .replace("OPEN", "")
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
