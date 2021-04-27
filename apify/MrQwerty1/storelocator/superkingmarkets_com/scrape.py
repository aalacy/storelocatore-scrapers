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


def get_urls():
    session = SgRequests()
    r = session.get("https://superkingmarkets.com/")
    tree = html.fromstring(r.text)

    return tree.xpath(
        "//a[./span[text()='Weekly Ad']]/following-sibling::div[1]//a/@href"
    )


def get_data(url):
    locator_domain = "https://superkingmarkets.com/"
    page_url = f"https://superkingmarkets.com{url}"

    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    location_name = "".join(tree.xpath("//h1/text()")).strip()
    line = tree.xpath("//span[./a[@class='btn btn-primary btn-sm']]/text()")
    line = list(filter(None, [l.strip() for l in line]))

    street_address = line.pop(0)
    csz = line.pop(0)
    city = csz.split(",")[0].strip()
    csz = csz.split(",")[1].strip()
    state = csz.split()[0]
    postal = csz.split()[1]
    hours_of_operation = line.pop(0)
    phone = line.pop(0).replace("Phone", "").replace(":", "").strip()
    country_code = "US"
    store_number = "<MISSING>"
    text = "".join(tree.xpath("//a[@class='btn btn-primary btn-sm']/@href"))
    if "embed" in text:
        latitude, longitude = get_coords_from_embed(text)
    else:
        latitude, longitude = get_coords_from_google_url(text)
    location_type = "<MISSING>"

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
