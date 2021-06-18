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
    r = session.get("https://www.tacofino.com/")
    tree = html.fromstring(r.text)

    return tree.xpath(
        "//li[@class='LocationsDropdown-locationItem']/div/a[@class='RestaurantCard']/@href"
    )


def get_data(page_url):
    locator_domain = "https://www.tacofino.com/"

    session = SgRequests()
    r = session.get(page_url)
    if r.status_code != 200:
        return
    tree = html.fromstring(r.text)

    location_name = "".join(tree.xpath("//h1/text()")).strip()
    line = tree.xpath(
        "//p[@class='RestaurantInfo-hours']/a/text()|//p[@class='RestaurantInfo-hours']/text()"
    )
    line = list(filter(None, [l.strip() for l in line]))

    if len(line) == 1:
        street_address = "<MISSING>"
        city = line[0].split(",")[0].strip()
        state = line[0].split(",")[1].strip()
        postal = "<MISSING>"
    else:
        street_address = line[0]
        city = line[1].split(",")[0].strip()
        state = line[1].split(",")[1].strip()
        if "BC " in state:
            state = state.replace("BC ", "")
        postal = line[-1]

    country_code = "CA"
    store_number = "<MISSING>"
    phone = (
        "".join(
            tree.xpath(
                "//p[@class='RestaurantInfo-phone']/a[contains(@href, 'tel')]/text()"
            )
        ).strip()
        or "<MISSING>"
    )
    latitude = (
        "".join(tree.xpath("//meta[@property='place:location:latitude']/@content"))
        or "<MISSING>"
    )
    longitude = (
        "".join(tree.xpath("//meta[@property='place:location:longitude']/@content"))
        or "<MISSING>"
    )
    if "." not in latitude:
        latitude, longitude = "<MISSING>", "<MISSING>"
    location_type = "<MISSING>"
    hours_of_operation = (
        " ".join(
            ";".join(tree.xpath("//meta[@itemprop='openingHours']/@content")).split()
        )
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

    with futures.ThreadPoolExecutor(max_workers=15) as executor:
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
