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
    r = session.get("https://good2gostores.com/locations")
    tree = html.fromstring(r.text)

    return tree.xpath("//h4/a/@href")


def get_data(page_url):
    locator_domain = "https://good2gostores.com/"
    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    location_name = "".join(tree.xpath("//h1[@class='col-xs-12']/text()")).strip()
    line = "".join(tree.xpath("//*[./i[@class='fa fa-location-arrow']]/text()")).strip()
    line = line.split(",")
    street_address = ", ".join(line[:-2]).strip() or "<MISSING>"
    city = line[-2].strip()
    part = line[-1].strip()
    state = part.split()[0]
    postal = part.split()[1]
    country_code = "US"
    store_number = (
        "".join(
            tree.xpath("//div[@class='col-xs-12' and contains(text(), '#')]/text()")
        )
        .strip()
        .replace("#", "")
    )
    phone = (
        "".join(tree.xpath("//a[./i[@class='fa fa-phone']]/text()")).strip()
        or "<MISSING>"
    )
    latitude = "".join(tree.xpath("//span[@data-lat]/@data-lat")) or "<MISSING>"
    longitude = "".join(tree.xpath("//span[@data-lat]/@data-lng")) or "<MISSING>"
    location_type = "<MISSING>"

    _tmp = []
    tr = tree.xpath("//table[@class='hours-table']//tr")

    for t in tr:
        day = "".join(t.xpath("./td[1]//text()")).strip()
        time = "".join(t.xpath("./td[2]//text()")).strip()
        _tmp.append(f"{day}: {time}")

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
