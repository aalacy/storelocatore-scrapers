import csv
import json

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
    geo = dict()
    urls = set()
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0"
    }
    r = session.get("https://www.1800packrat.com/locations", headers=headers)
    tree = html.fromstring(r.text)
    text = (
        "".join(tree.xpath("//script[contains(text(), 'markers:')]/text()"))
        .split("markers:")[1]
        .split("]")[0]
        .strip()[:-1]
        + "]"
    )
    js = json.loads(text)
    for j in js:
        url = j.get("Link").replace(
            "/sites/packrat/home", "https://www.1800packrat.com"
        )
        urls.add(url)
        slug = url.split("/")[-1]
        lat = j.get("Latitude") or "<MISSING>"
        lng = j.get("Longitude") or "<MISSING>"
        geo[slug] = {"lat": lat, "lng": lng}

    return urls, geo


def get_data(page_url, geo):
    rows = []
    locator_domain = "https://www.1800packrat.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:84.0) Gecko/20100101 Firefox/84.0"
    }
    key = page_url.split("/")[-1]
    session = SgRequests()
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)

    location_name = "".join(tree.xpath("//h1/text()")).strip()
    country_code = "US"
    store_number = "<MISSING>"
    latitude = geo[key].get("lat")
    longitude = geo[key].get("lng")
    location_type = "<MISSING>"
    hours_of_operation = (
        ";".join(tree.xpath("//p[contains(text(), 'CUSTOMER SERVICE HOURS')]/text()"))
        .replace("\n", "")
        .replace("CUSTOMER SERVICE HOURS;", "")
        or "<MISSING>"
    )

    lines = tree.xpath(
        "//p[contains(text(), 'CUSTOMER SERVICE HOURS')]/preceding-sibling::p"
    )
    for l in lines:
        line = l.xpath(".//text()")
        line = list(filter(None, [li.strip() for li in line]))
        street_address = ", ".join(line[:-2])
        phone = line[-1]
        line = line[-2]
        city = line.split(",")[0].strip()
        line = line.split(",")[1].strip()
        state = line.split()[0]
        try:
            postal = line.split()[1]
        except IndexError:
            postal = "<MISSING>"

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

        rows.append(row)

    return rows


def fetch_data():
    out = []
    urls, geo = get_urls()

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_data, url, geo): url for url in urls}
        for future in futures.as_completed(future_to_url):
            rows = future.result()
            for row in rows:
                out.append(row)

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
