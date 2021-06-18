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
    r = session.get("https://gasserhardware.com/")
    tree = html.fromstring(r.text)

    return tree.xpath(
        "//ul[@id='main-nav']//a[./span[text()='Locations']]/following-sibling::ul//a/@href"
    )


def get_coords_from_embed(text):
    if "bing" in text:
        text = text.split("cp=")[1].split("&")[0]
        return text.split("~")
    try:
        latitude = text.split("!3d")[1].strip().split("!")[0].strip()
        longitude = text.split("!2d")[1].strip().split("!")[0].strip()
    except IndexError:
        latitude, longitude = "<MISSING>", "<MISSING>"

    return latitude, longitude


def get_data(page_url):
    locator_domain = "https://gasserhardware.com/"

    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    location_name = "".join(tree.xpath("//h1/text()")).strip()
    line = tree.xpath("//div[./b or ./strong]/text()|//p[./strong]/text()")
    if not line:
        line = tree.xpath("//div[@class='wpb_wrapper']/p[1]/text()")[1:]
    line = list(filter(None, [l.strip() for l in line]))

    street_address = ", ".join(line[:-1])
    line = line[-1]
    city = line.split(",")[0].strip()
    line = line.split(",")[1].strip()
    state = line.split()[0]
    postal = line.split()[1]
    country_code = "US"
    store_number = "<MISSING>"
    phone = "<MISSING>"
    lines = tree.xpath("//div[@class='wpb_wrapper']//text()")
    for line in lines:
        if "Phone:" in line:
            phone = line.replace("Phone:", "").strip()
            break

    text = "".join(tree.xpath("//iframe/@src"))
    latitude, longitude = get_coords_from_embed(text)
    location_type = "<MISSING>"

    hours = tree.xpath("//p[contains(text(),'Hours:')]/text()")
    hours = list(filter(None, [h.strip() for h in hours]))
    hours.remove("Hours:")
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
