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
    session = SgRequests()
    r = session.get("https://www.thorntons.co.uk/store-locator/")
    tree = html.fromstring(r.text)

    return tree.xpath("//ul[@class='alphabet-stores-list']//a/@href")


def get_data(page_url):
    locator_domain = "https://www.thorntons.co.uk/"

    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)
    text = "".join(tree.xpath("//div[@data-store]/@data-store"))
    j = json.loads(text)

    location_name = j.get("name")
    street_address = j.get("address1") or "<MISSING>"
    city = j.get("city") or "<MISSING>"
    state = j.get("stateCode") or "<MISSING>"
    postal = j.get("postalCode") or "<MISSING>"
    country_code = "GB"
    store_number = j.get("ID") or "<MISSING>"
    phone = j.get("phone") or "<MISSING>"
    geo = j.get("coordinates") or {}
    latitude = geo.get("lat") or "<MISSING>"
    longitude = geo.get("lng") or "<MISSING>"
    location_type = j.get("shopType") or "<MISSING>"
    if location_type.find("This") != -1:
        location_type = "<MISSING>"

    _tmp = []
    days = j.get("openning", {}).get("days") or []

    for d in days:
        day = d.get("name")
        time = d.get("time")
        _tmp.append(f"{day}: {time}")

    hours_of_operation = ";".join(_tmp) or "<MISSING>"
    isclosed = tree.xpath(
        "//div[@style='width:100%; padding: 1em; background: red; color: white; font-size: 16px; display: flex; align-items: center; justify-content: center;margin-bottom: 2em; box-sizing: border-box;']"
    )

    if isclosed:
        hours_of_operation = "Closed"

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
