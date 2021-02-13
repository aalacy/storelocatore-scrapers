import csv
import re

from concurrent import futures
from lxml import html
from sgrequests import SgRequests
from sgzip.static import static_coordinate_list, SearchableCountries
from sgscrape.sgpostal import parse_address, International_Parser


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


def get_urls(coord):
    urls = []
    api_url = "https://heronfoods.com/index.php"

    data = {
        "params": "eyJyZXN1bHRfcGFnZSI6InN0b3JlbG9jYXRvciJ9",
        "ACT": "29",
        "site_id": "1",
        "distance:from": "|".join(coord),
    }

    session = SgRequests()
    r = session.post(api_url, data=data)
    u = r.url

    for i in range(0, 60000, 6):
        url = f"{u}/P{i}"
        r = session.get(url)
        tree = html.fromstring(r.text.replace("<!--p>", "").replace("</p-->", ""))
        divs = tree.xpath("//div[contains(@class, 'box2col store-details-container')]")
        for d in divs:
            page_url = "".join(
                d.xpath(".//a[contains(@href, '/store-details/')]/@href")
            )
            urls.append(page_url)

        if len(divs) < 6:
            break

    return urls


def get_data(page_url):
    locator_domain = "https://heronfoods.com/"

    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    location_name = "".join(tree.xpath("//h1/text()")).strip()
    line = tree.xpath("//div[@class='box2col store-details']/p/text()")
    line = list(filter(None, [l.strip() for l in line]))
    line = " ".join(line)
    adr = parse_address(International_Parser(), line)

    street_address = (
        f"{adr.street_address_1} {adr.street_address_2 or ''}".replace(
            "None", ""
        ).strip()
        or "<MISSING>"
    )

    city = adr.city or "<MISSING>"
    state = adr.state or "<MISSING>"
    postal = adr.postcode or "<MISSING>"
    country_code = "GB"
    store_number = "<MISSING>"
    phone = "<MISSING>"
    text = "".join(tree.xpath("//div[@class='box-wrapper']//script/text()"))
    latitude = "".join(re.findall(r'"lat":"(\d+.\d+)', text)) or "<MISSING>"
    longitude = "".join(re.findall(r'"lng":"(-?\d+.\d+)', text)) or "<MISSING>"
    location_type = "<MISSING>"

    _tmp = []
    li = tree.xpath("//div[@class='box2col opening-hours']//li")
    for l in li:
        day = "".join(l.xpath("./text()|./strong/text()")).strip()
        time = "".join(l.xpath("./span/text()|./strong/span/text()")).strip()
        _tmp.append(f"{day}: {time}")

    hours_of_operation = ";".join(_tmp) or "<MISSING>"
    iscoming = tree.xpath("//p[@class='new-store']")
    if iscoming:
        hours_of_operation = "Coming Soon"

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
    coords = static_coordinate_list(radius=15, country_code=SearchableCountries.BRITAIN)
    urls = set()

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_urls, coord): coord for coord in coords}
        for future in futures.as_completed(future_to_url):
            links = future.result()
            for link in links:
                urls.add(link)

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
