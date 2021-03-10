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
    r = session.get("https://barmethod.com/locations/")
    tree = html.fromstring(r.text)

    return tree.xpath("//a[@class='studioname']/@href")


def get_data(page_url):
    locator_domain = "https://barmethod.com/"

    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    location_name = (
        "".join(tree.xpath("//h1[@class='mtn']/text()")).strip() or "<MISSING>"
    )

    # permanently closed
    if location_name == "<MISSING>":
        return

    line = tree.xpath("//address/text()")
    line = list(filter(None, [l.strip() for l in line]))
    street_address = line[0]
    if street_address.find("(") != -1:
        street_address = street_address.split("(")[0].strip()
    line = line[-1]
    city = line.split(",")[0].strip()
    line = line.split(",")[1].strip()
    state = line.split()[0].strip()
    postal = line.replace(state, "").strip()
    if len(postal) == 5:
        country_code = "US"
    else:
        country_code = "CA"

    store_number = "<MISSING>"
    phone = "".join(tree.xpath("//a[@id='phone-number']/text()")).strip() or "<MISSING>"
    latitude = "<MISSING>"
    longitude = "<MISSING>"
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
