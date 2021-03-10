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
    r = session.get("https://www.doodlebugs.com/request-a-tour/")
    tree = html.fromstring(r.text)

    return tree.xpath(
        "//ul[@class='list-reset']//a[contains(@href, '/location/')]/@href"
    )


def get_data(page_url):
    locator_domain = "https://www.doodlebugs.com/"

    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    location_name = "".join(
        tree.xpath("//h2[@class='dark-blue-text text-uppercase']/text()")
    ).strip()
    line = tree.xpath(
        "//p[@class='subheading-font subheading-size not-google-maps']/text()"
    )
    street_address = ", ".join(line[:-1])
    line = line[-1]
    postal = line.split(",")[-1].strip()
    if len(line.split(",")) == 2:
        line = line.split(",")[0].strip()
        city = " ".join(line.split()[:-1])
        state = line.split()[-1]
    else:
        city = line.split(",")[0].strip()
        state = line.split(",")[1].strip()
    country_code = "US"
    store_number = "<MISSING>"
    phone = "".join(tree.xpath("//div[@data-lat]/@data-phone")) or "<MISSING>"
    latitude = "".join(tree.xpath("//div[@data-lat]/@data-lat")) or "<MISSING>"
    longitude = "".join(tree.xpath("//div[@data-lat]/@data-lng")) or "<MISSING>"
    location_type = "<MISSING>"
    check = "".join(
        tree.xpath(
            "//h3[@class='subheading-font subheading-size subheading-margin dark-blue-text']/text()"
        )
    )
    if check.lower().find("coming") != -1:
        location_type = "Coming Soon"
    hours_of_operation = (
        "".join(
            tree.xpath("//p[@class='text-lg' and contains(text(), 'Hours')]/text()")
        ).strip()
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
