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
    r = session.get("https://www.eatpdq.com/Widgets/LocationSearchResult.ashx")
    tree = html.fromstring(r.content)

    return tree.xpath("//marker/@href")


def get_data(page_url):
    locator_domain = "https://www.eatpdq.com/"

    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    location_name = "".join(tree.xpath("//div[@class='name']/h1/text()")).strip()
    line = tree.xpath("//div[@class='address']/text()")
    line = list(filter(None, [l.strip() for l in line]))
    street_address = line[0]
    line = line[-1]
    city = line.split(",")[0].strip()
    line = line.split(",")[1].strip()
    state = line.split()[0].strip()
    postal = line.split()[1].strip()
    country_code = "US"
    store_number = "<MISSING>"
    phone = "".join(tree.xpath("//tel/a/text()")).strip() or "<MISSING>"
    _map = "".join(
        tree.xpath(
            "//div[@class='address']/a[contains(@href, 'google.com/maps/')]/@href"
        )
    )
    if _map:
        line = _map.split("@")[-1]
        latitude = line.split(",")[0] or "<MISSING>"
        longitude = line.split(",")[1] or "<MISSING>"
    else:
        latitude = "<MISSING>"
        longitude = "<MISSING>"

    location_type = "<MISSING>"
    hours = "".join(tree.xpath("//div[@class='hours']//h2/text()")).strip()

    if hours and hours.find("OPEN") == -1:
        hours_of_operation = f"Mon-Sun: {hours}"
    elif hours == "":
        hours_of_operation = (
            "".join(tree.xpath("//div[@class='hours']//p//text()"))
            .replace("\n\n", ";")
            .replace("\n", " ")
            .strip()
        )
    else:
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
