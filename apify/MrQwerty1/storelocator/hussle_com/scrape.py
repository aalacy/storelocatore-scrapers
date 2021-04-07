import csv
import json

from concurrent import futures
from lxml import html
from sgrequests import SgRequests
from sgzip.static import static_zipcode_list, SearchableCountries


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


def get_urls(postal):
    urls = []
    session = SgRequests()
    for i in range(1, 5000):
        r = session.get(
            f"https://www.hussle.com/search?distance=20&geo-location=&location={postal}&page={i}"
        )

        tree = html.fromstring(r.text)
        links = tree.xpath("//a[@class='result__gym-name-link']/@href")
        for l in links:
            urls.append(f"https://www.hussle.com{l}")

        if len(links) < 20:
            break

    return urls


def get_data(page_url):
    locator_domain = "https://www.hussle.com/"
    session = SgRequests()
    r = session.get(page_url)

    if page_url != r.url:
        return

    tree = html.fromstring(r.text)
    text = "".join(tree.xpath("//script[@id='__NEXT_DATA__']/text()"))
    j = json.loads(text)["props"]["pageProps"]["data"]

    location_name = j.get("name")
    phone = j.get("telephone") or "<MISSING>"
    if phone == "<MISSING>":
        t = "".join(tree.xpath("//div[@class='Banner_banner__content__1lZbw']/text()"))
        if "phone" in t and "details:" in t:
            phone = t.split("details:")[-1].replace(".", "").strip()

    country_code = "GB"
    store_number = j.get("id") or "<MISSING>"
    location_type = "<MISSING>"

    a = j.get("location") or {}
    street_address = a.get("street_address") or "<MISSING>"
    city = a.get("locality") or "<MISSING>"
    state = "<MISSING>"
    postal = a.get("postcode") or "<MISSING>"
    latitude = a.get("latitude") or "<MISSING>"
    longitude = a.get("longitude") or "<MISSING>"

    _tmp = []
    days = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ]
    hours = j.get("opening_times") or {}
    for d, t in zip(days, hours.values()):
        start = t.get("opens_at")
        close = t.get("closes_at")
        _tmp.append(f"{d}: {start} - {close}")

    hours_of_operation = ";".join(_tmp) or "<MISSING>"

    if j.get("is_temporarily_closed"):
        location_type = "Temporarily Closed"

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
    urls = set()

    postals = static_zipcode_list(radius=20, country_code=SearchableCountries.BRITAIN)
    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_urls, p): p for p in postals}
        for future in futures.as_completed(future_to_url):
            links = future.result()
            for l in links:
                urls.add(l)

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
