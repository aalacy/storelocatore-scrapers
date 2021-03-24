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
    r = session.get("https://mayweather.fit/locations/")
    tree = html.fromstring(r.text)
    divs = tree.xpath("//div[@class='block col-12 col-sm-4 col-md-3']")
    for d in divs:
        check = "".join(d.xpath(".//text()"))
        if "COMING SOON" in check:
            continue

        url = "".join(d.xpath(".//a[@class='btn btn-hollow light']/@href"))
        if url:
            urls.append(url)

    return urls


def get_data(page_url):
    locator_domain = "https://mayweather.fit/"

    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)
    if tree.xpath("//span[text()='COMING SOON']"):
        return

    location_name = "".join(
        tree.xpath("//div[@class='locationBox col-auto']/h4/text()")
    ).strip()
    line = tree.xpath("//div[@class='locationBox col-auto']/p[1]/text()")
    line = list(filter(None, [l.strip() for l in line]))

    street_address = ", ".join(line[:-1]).strip()
    line = line[-1]
    city = line.split(",")[0].strip()
    line = line.split(",")[1].strip()
    state = line.split()[0]
    postal = line.split()[1]
    country_code = "US"
    store_number = "<MISSING>"
    phone = (
        "".join(
            tree.xpath(
                "//div[@class='col-12 col-sm-4']/a[contains(@href, 'tel')]/text()"
            )
        ).strip()
        or "<MISSING>"
    )
    latitude = "".join(tree.xpath("//div[@data-lat]/@data-lat")) or "<MISSING>"
    longitude = "".join(tree.xpath("//div[@data-lat]/@data-lng")) or "<MISSING>"
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
