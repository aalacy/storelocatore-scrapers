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
    r = session.get("https://www.dandanrestaurant.com/")
    tree = html.fromstring(r.text)

    return set(tree.xpath("//li/a[contains(@href, '/location/')]/@href"))


def get_data(url):
    locator_domain = "https://www.dandanrestaurant.com/"
    page_url = f"https://www.dandanrestaurant.com{url}"

    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    location_name = "".join(tree.xpath("//h1/text()")).strip()
    line = tree.xpath("//div[@class='col-md-6']/p/a[contains(@href, 'google')]/text()")
    line = list(filter(None, [l.strip() for l in line]))

    street_address = ", ".join(line[:-1])
    line = line[-1]
    city = line.split(",")[0].strip()
    line = line.split(",")[1].strip()
    state = line.split()[0]
    postal = line.split()[1]
    country_code = "US"
    store_number = "<MISSING>"
    phone = (
        "".join(tree.xpath("//a[contains(@href, 'tel:')]/text()")).strip()
        or "<MISSING>"
    )
    latitude = (
        "".join(tree.xpath("//div[@data-gmaps-lat]/@data-gmaps-lat")) or "<MISSING>"
    )
    longitude = (
        "".join(tree.xpath("//div[@data-gmaps-lat]/@data-gmaps-lng")) or "<MISSING>"
    )
    location_type = "<MISSING>"

    _tmp = []
    hours = tree.xpath("//p[./a[contains(@href, 'tel:')]]/following-sibling::p/text()")
    for h in hours:
        if "happy" in h.lower():
            break
        if "hour" in h.lower() or not h.strip():
            continue
        _tmp.append(h.strip())

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

    with futures.ThreadPoolExecutor(max_workers=2) as executor:
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
