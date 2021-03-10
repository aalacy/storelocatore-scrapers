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
    r = session.get("https://www.thrifty.co.uk/locations.htm")
    tree = html.fromstring(r.text)

    return set(tree.xpath("//ul[@class='locations']/li/a/@href"))


def get_data(url):
    locator_domain = "https://www.thrifty.co.uk/"
    page_url = f"https://www.thrifty.co.uk{url}"

    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    location_name = "".join(
        tree.xpath("//div[@class='rightcol_book_inner']/p/strong/text()")
    ).strip()
    line = tree.xpath("//div[@class='rightcol_book_inner']/p/text()")
    line = list(filter(None, [l.strip() for l in line]))

    try:
        street_address = ", ".join(line[:-2])
        city = line[-2]
        postal = line[-1]
    except IndexError:
        street_address = "<MISSING>"
        city = "<MISSING>"
        postal = "<MISSING>"

    state = "<MISSING>"
    if city.lower().find("park,") != -1:
        city = city.split(",")[-1].strip()
    if city.find(",") != -1:
        state = city.split(",")[-1].strip() or "<MISSING>"
        city = city.split(",")[0].strip()

    country_code = "GB"
    store_number = "<MISSING>"
    text = "".join(tree.xpath("//div[@class='book_outer']/text()")).strip()
    try:
        phone = text.split("call")[-1].split("*")[0].strip() or "<MISSING>"
        if phone.find("\n") != -1:
            if phone.find("dial") != -1:
                phone = phone.split("dial")[1].split("*")[0].strip()
            else:
                phone = "<MISSING>"
    except IndexError:
        phone = "<MISSING>"

    latitude = "<MISSING>"
    longitude = "<MISSING>"
    location_type = "<MISSING>"

    _tmp = []
    days = tree.xpath("//span[@class='res_left_locations']/text()")
    times = tree.xpath("//span[@class='res_right_locations']/text()")

    for d, t in zip(days, times):
        _tmp.append(f"{d.strip()}: {t.strip()}")

    hours_of_operation = ";".join(_tmp) or "<MISSING>"
    if hours_of_operation.count("Closed") == 7:
        hours_of_operation = "Closed"

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
