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
    r = session.get("https://www.pollyspies.com/locations/")
    tree = html.fromstring(r.text)

    return tree.xpath("//a[@class='location-details loc_cta']/@href")


def get_data(page_url):
    locator_domain = "https://www.pollyspies.com/"

    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    location_name = "".join(tree.xpath("//h1/span/text()")).strip()
    line = tree.xpath("//div[@class='address']/a[1]/text()")
    line = list(filter(None, [l.strip() for l in line]))

    street_address = line[0]
    line = line[-1]
    city = line.split(",")[0].strip()
    state = line.split(",")[1].strip()
    postal = line.split(",")[-1].strip()
    country_code = "US"
    store_number = "<MISSING>"
    phone = (
        "".join(tree.xpath("//div[@class='telephone']/a/text()")).strip() or "<MISSING>"
    )

    text = "".join(
        tree.xpath("//script[contains(text(), 'var single_location_lat = ')]/text()")
    )
    latitude = text.split("var single_location_lat = ")[1].split(";")[0]
    longitude = text.split("var single_location_lng = ")[1].split(";")[0]
    location_type = "<MISSING>"

    _tmp = []
    divs = tree.xpath("//div[@class='hours_block']")

    for d in divs:
        day = "".join(d.xpath("./span/text()")).strip()
        time = "".join(d.xpath("./text()")).strip()
        _tmp.append(f"{day} {time}")

    hours_of_operation = ";".join(_tmp) or "<MISSING>"

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
