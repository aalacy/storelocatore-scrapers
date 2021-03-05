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
    urls = []
    session = SgRequests()

    for i in range(1, 5000):
        r = session.get(f"https://www.binswangerglass.com/branch/page/{i}/")
        tree = html.fromstring(r.text)
        links = tree.xpath("//a[@rel='bookmark']/@href")
        urls += links

        if len(links) < 12:
            break

    return urls


def get_data(page_url):
    locator_domain = "https://www.binswangerglass.com/"

    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    line = tree.xpath("//address/text()")
    line = list(filter(None, [l.strip() for l in line]))
    location_name = " ".join(
        "".join(tree.xpath("//div[@class=' loc-content-text']/h3/text()")).split()
    )
    street_address = ", ".join(line[:-1])
    line = line[-1]
    city = line.split(",")[0].strip()
    line = line.split(",")[1].strip()
    state = line.split()[0]
    postal = line.split()[1]
    country_code = "US"
    store_number = location_name.split("#")[-1]
    phone = (
        "".join(
            tree.xpath("//a[@class='font-weight-bold color-phone-link mb-2']/text()")
        ).strip()
        or "<MISSING>"
    )
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    location_type = "<MISSING>"

    _tmp = []
    pp = tree.xpath("//div[@class='location-info-hours']/p")

    for p in pp:
        _tmp.append(f'{"".join(p.xpath(".//text()")).strip()}')

    hours_of_operation = ";".join(_tmp) or "<MISSING>"
    if hours_of_operation.find("contact") != -1:
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
