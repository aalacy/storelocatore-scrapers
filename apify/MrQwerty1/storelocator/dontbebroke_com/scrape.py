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
    session = SgRequests()
    r = session.get("https://www.dontbebroke.com/locations-nearest-you/")
    tree = html.fromstring(r.text)
    states = tree.xpath("//a[@class='button yellow']/@href")
    for state in states:
        r = session.get(f"https://www.dontbebroke.com{state}")
        tree = html.fromstring(r.text)
        slugs = tree.xpath("//div[@class='locations-by-city-container']//a/@href")
        for slug in slugs:
            urls.append(f"https://www.dontbebroke.com/page-data{slug}/page-data.json")

    return urls


def get_data(url):
    locator_domain = "https://www.dontbebroke.com/"

    session = SgRequests()
    r = session.get(url)
    j = r.json()["result"]["data"]["wpgraphql"]["location"]["location"]

    street_address = (
        f'{j.get("address")} {j.get("address2") or ""}'.strip() or "<MISSING>"
    )
    city = j.get("city") or "<MISSING>"
    state = j.get("state") or "<MISSING>"
    postal = j.get("postalCode") or "<MISSING>"
    country_code = "US"
    store_number = "<MISSING>"
    page_url = url.replace("/page-data", "").replace(".json", "")
    location_name = j.get("title")
    phone = j.get("phone") or "<MISSING>"
    latitude = j.get("latitude") or "<MISSING>"
    longitude = j.get("longitude") or "<MISSING>"
    location_type = "<MISSING>"

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

    for d in days:
        time = j.get(d.lower())
        _tmp.append(f"{d}: {time}")

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
