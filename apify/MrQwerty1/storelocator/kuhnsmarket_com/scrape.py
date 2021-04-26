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


def get_coords_from_google_url(url):
    try:
        latitude, longitude = url.split("%40")[1].split("'")[0].split(",")
    except IndexError:
        latitude, longitude = "<MISSING>", "<MISSING>"

    return latitude, longitude


def get_urls():
    session = SgRequests()
    r = session.get("https://kuhnsmarket.com/locations/")
    tree = html.fromstring(r.text)

    return tree.xpath("//area[@class='pins']/@href")


def get_data(url):
    locator_domain = "https://kuhnsmarket.com/"
    page_url = f"https://kuhnsmarket.com/locations/{url}"

    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    location_name = "".join(
        tree.xpath("//span/i[not(contains(text(), 'Manager'))]/text()")
    ).strip()
    line = tree.xpath("//div[@id='locationhdr']/div/span/text()")
    line = list(filter(None, [l.strip() for l in line]))

    street_address = line[0]
    phone = line[-1]
    line = line[1]
    city = line.split(",")[0].strip()
    line = line.split(",")[1].strip()
    state = line.split()[0]
    postal = line.split()[1]
    country_code = "US"
    store_number = "<MISSING>"
    text = "".join(tree.xpath("//img[contains(@onclick, 'maps')]/@onclick"))
    latitude, longitude = get_coords_from_google_url(text)
    location_type = "<MISSING>"
    hours_of_operation = (
        "".join(tree.xpath("//b[contains(text(), 'Store Hours')]/text()"))
        .replace("Store Hours:", "")
        .replace("Open", "")
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
    scrape()
