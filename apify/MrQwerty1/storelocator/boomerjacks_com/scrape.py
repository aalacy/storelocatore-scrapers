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
    coords = []
    session = SgRequests()
    r = session.get(
        "https://boomerjacks.com/wp-json/wpgmza/v1/features/base64eJyrVkrLzClJLVKyUqqOUcpNLIjPTIlRsopRMopR0gEJFGeUFni6FAPFomOBAsmlxSX5uW6ZqTkpELFapVoABXgWuw"
    )
    js = r.json()["markers"]
    for j in js:
        lat = j.get("lat") or "<MISSING>"
        lng = j.get("lng") or "<MISSING>"
        coords.append((lat, lng))
        source = j.get("description")
        tree = html.fromstring(source)
        urls.append(tree.xpath("//a[contains(@href, '/locations/')]/@href")[0])

    return coords, urls


def get_data(page_url, coords):
    locator_domain = "https://boomerjacks.com/"

    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    location_name = " ".join("".join(tree.xpath("//h1/text()")).split())
    line = tree.xpath(
        "//h1/following-sibling::p[1]/text()|//p[@class='formatted_content']/text()"
    )
    line = list(filter(None, [l.strip() for l in line]))
    if len(line) == 1:
        line = ["".join(line[0].split(",")[0]), ",".join(line[0].split(",")[1:])]

    street_address = line[0].strip()
    line = line[1].replace(",", "")
    postal = line.split()[-1]
    state = line.split()[-2]
    city = line.replace(state, "").replace(postal, "").strip()
    country_code = "US"
    store_number = "<MISSING>"
    phone = (
        "".join(
            tree.xpath(
                "//h1/following-sibling::p[2]/text()|//p[@class='formatted_content']/following-sibling::p[1]/text()"
            )
        ).strip()
        or "<MISSING>"
    )
    latitude, longitude = coords
    location_type = "<MISSING>"
    if location_name.find("COMING") != -1:
        location_type = "Coming Soon"
    hours_of_operation = (
        ";".join(
            tree.xpath(
                "//h1/following-sibling::p[3]/text()|//p[@class='formatted_content']/following-sibling::p[3]/text()"
            )
        )
        .replace("\n", "")
        .strip()
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
    coords, urls = get_urls()

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {
            executor.submit(get_data, url, coord): (url, coord)
            for url, coord in zip(urls, coords)
        }
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
