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
    r = session.get("https://lebakkensrto.com/locations")
    tree = html.fromstring(r.text)

    return tree.xpath("//a[@class='btn btn-primary']/@href")


def get_data(url):
    locator_domain = "https://lebakkensrto.com/"
    page_url = f"https://lebakkensrto.com{url}"

    session = SgRequests()
    r = session.get(page_url)
    source = r.text.replace("<!--", "").replace("-->", "")
    tree = html.fromstring(source)

    location_name = "".join(tree.xpath("//p[./strong[text()='name']]/text()")).replace(
        ": ", ""
    )
    street_address = (
        "".join(tree.xpath("//p[./strong[text()='address']]/text()")).replace(": ", "")
        or "<MISSING>"
    )
    city = (
        "".join(tree.xpath("//p[./strong[text()='city']]/text()")).replace(": ", "")
        or "<MISSING>"
    )
    state = (
        "".join(tree.xpath("//p[./strong[text()='state']]/text()")).replace(": ", "")
        or "<MISSING>"
    )
    postal = (
        "".join(tree.xpath("//p[./strong[text()='zipcode']]/text()")).replace(": ", "")
        or "<MISSING>"
    )
    country_code = "US"
    store_number = (
        "".join(tree.xpath("//p[./strong[text()='id']]/text()")).replace(": ", "")
        or "<MISSING>"
    )
    phone = (
        "".join(tree.xpath("//p[./strong[text()='phone_number']]/text()")).replace(
            ": ", ""
        )
        or "<MISSING>"
    )
    latitude = (
        "".join(tree.xpath("//p[./strong[text()='latitude']]/text()")).replace(": ", "")
        or "<MISSING>"
    )
    longitude = (
        "".join(tree.xpath("//p[./strong[text()='longitude']]/text()")).replace(
            ": ", ""
        )
        or "<MISSING>"
    )
    location_type = "<MISSING>"
    hours_of_operation = (
        "".join(tree.xpath("//p[./strong[text()='hours']]/text()"))
        .replace(": ", "")
        .replace("<br>", ";")
        or "<MISSING>"
    )

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
