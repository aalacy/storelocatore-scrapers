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


def get_coords_from_embed(text):
    try:
        latitude = text.split("!3d")[1].strip().split("!")[0].strip()
        longitude = text.split("!2d")[1].strip().split("!")[0].strip()
    except IndexError:
        latitude, longitude = "<MISSING>", "<MISSING>"

    return latitude, longitude


def get_urls():
    session = SgRequests()
    r = session.get("https://www.farmandhomesupply.com/company/store-locations/")
    tree = html.fromstring(r.text)

    return set(tree.xpath("//div[@class='store-grid-content']/a/@href"))


def get_data(url):
    locator_domain = "https://www.farmandhomesupply.com/"
    page_url = f"https://www.farmandhomesupply.com{url}"

    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    location_name = "".join(tree.xpath("//h1/text()")).strip()
    line = tree.xpath("//p[./a]/text()")
    line = list(filter(None, [l.strip() for l in line]))

    street_address = line[0]
    line = line[1].replace(",", "")
    postal = line.split()[-1]
    state = line.split()[-2]
    city = line.replace(state, "").replace(postal, "").strip()
    country_code = "US"
    store_number = "<MISSING>"
    phone = (
        "".join(tree.xpath("//p[./a]/a[contains(@href,'tel')]/text()")).strip()
        or "<MISSING>"
    )

    text = "".join(tree.xpath("//p/iframe/@src"))
    latitude, longitude = get_coords_from_embed(text)
    location_type = "<MISSING>"

    hours = tree.xpath(
        "//p[text()='Hours:']/following-sibling::p[1]/text()|//p[./*[text()='Hours:']]/following-sibling::p[1]/text()"
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
