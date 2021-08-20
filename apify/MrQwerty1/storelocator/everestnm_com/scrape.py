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
    r = session.get("https://everestnm.com/")
    tree = html.fromstring(r.text)

    return set(
        tree.xpath(
            "//div[./div/h4[contains(text(), 'locations')]]/following-sibling::div[1]//a/@href"
        )
    )


def get_id(page_url):
    r = session.get(page_url)
    tree = html.fromstring(r.text)
    text = "".join(
        tree.xpath(
            "//script[contains(text(), 'https://www.iheartjane.com/embed/stores/')]/text()"
        )
    )
    _id = text.split("https://www.iheartjane.com/embed/stores/")[1].split("/")[0]

    return _id


def get_data(page_url):
    locator_domain = "https://everestnm.com/"

    store_number = get_id(page_url)
    api = f"https://www.iheartjane.com/api/v1/stores/{store_number}?"
    r = session.get(api)
    j = r.json()["store"]

    location_name = j.get("name")
    street_address = j.get("address")
    city = j.get("city")
    state = j.get("state")
    postal = j.get("zip")
    country_code = "US"
    phone = j.get("phone") or "<MISSING>"
    latitude = j.get("lat") or "<MISSING>"
    longitude = j.get("long") or "<MISSING>"
    location_type = "<MISSING>"

    _tmp = []
    hours = j.get("working_hours") or []

    for h in hours:
        day = h.get("day")
        start = h["period"]["from"]
        end = h["period"]["to"]
        _tmp.append(f"{day}: {start} - {end}")

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
    session = SgRequests()
    scrape()
