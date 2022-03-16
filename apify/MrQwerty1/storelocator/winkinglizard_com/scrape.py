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
    r = session.get("https://winkinglizard.com/locations")
    tree = html.fromstring(r.text)

    return tree.xpath("//a[@class='button' and contains(@href, '/locations/')]/@href")


def get_data(page_url):
    locator_domain = "https://winkinglizard.com/"

    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    location_name = "".join(tree.xpath("//h1/span/text()")).strip()
    line = tree.xpath("//div[@class='medium-6 columns']/p[1]/preceding-sibling::text()")
    line = list(filter(None, [l.strip() for l in line]))
    street_address = ", ".join(line[:-1]).strip() or "<MISSING>"
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
                "//strong[contains(text(), 'Phone')]/following-sibling::text()[1]"
            )
        ).strip()
        or "<MISSING>"
    )

    text = "".join(tree.xpath("//div[@class='medium-6 columns']/p[1]/a/@href"))
    latitude, longitude = text.split("=")[-1].split(",")
    location_type = "<MISSING>"

    _tmp = []
    strong = tree.xpath(
        "//div[@class='medium-6 columns']/strong[last()]/preceding-sibling::strong"
    )

    for s in strong:
        day = "".join(s.xpath("./text()")).strip()
        time = "".join(s.xpath("./following-sibling::text()[1]"))
        if "(" in time:
            time = time.split("(")[0].strip()
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
