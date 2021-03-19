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
    r = session.get("https://adamsdrugs.net/adams-drugs-locations/")
    tree = html.fromstring(r.text)

    return set(tree.xpath("//a[contains(@href, '/locations/')]/@href"))


def get_data(page_url):
    locator_domain = "https://adamsdrugs.net/"

    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    location_name = "".join(tree.xpath("//h1/text()")).strip()
    street_address = "".join(
        tree.xpath("//h2[text()='Contact']/following-sibling::div[1]/p/a/text()")
    ).strip()
    line = tree.xpath("//h2[text()='Contact']/following-sibling::div[1]/p/text()")
    line = list(filter(None, [l.strip() for l in line]))
    line = line[0]
    city = line.split(",")[0].strip()
    line = line.split(",")[1].strip()
    state = line.split()[0]
    postal = line.split()[1]
    country_code = "US"
    store_number = "<MISSING>"
    phone = (
        "".join(
            tree.xpath(
                "//h2[text()='Contact']/following-sibling::div[1]/p/strong/text()"
            )
        ).strip()
        or "<MISSING>"
    )
    phone = phone.replace("Phone", "").replace("Ph", "").replace(":", "").strip()

    text = "".join(tree.xpath("//iframe/@data-src"))
    latitude, longitude = get_coords_from_embed(text)
    location_type = "<MISSING>"

    hours = tree.xpath("//h2[text()='Hours']/following-sibling::div[1]/p/text()")
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

    with futures.ThreadPoolExecutor(max_workers=12) as executor:
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
