import csv
import re

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
    r = session.get("https://expstores.com/", headers=headers)
    tree = html.fromstring(r.text)

    return tree.xpath("//a[contains(@class, 'mpfy-pin mpfy-pin-id-')]/@href")


def get_data(page_url):
    locator_domain = "https://expstores.com/"

    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)

    location_name = "".join(tree.xpath("//h1/text()")).strip()
    line = tree.xpath("//div[@class='mpfy-p-entry']//text()")
    line = list(filter(None, [l.replace("US", "").strip() for l in line]))

    phone = line.pop()
    street_address = line.pop(0)
    line = line[-1]
    postal = "".join(p.findall(line))
    state = "".join(st.findall(line))
    city = line.replace(postal, "").replace(state, "").strip()
    country_code = "US"
    store_number = "<MISSING>"
    text = "".join(tree.xpath("//a/@href"))
    latitude, longitude = text.split("=")[-1].split(",")
    location_type = "<MISSING>"
    hours_of_operation = "<MISSING>"

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
    headers = {
        "accept": "text/html, */*; q=0.01",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36",
        "x-requested-with": "XMLHttpRequest",
    }
    session = SgRequests()
    st = re.compile(r"[A-Z]{2}")
    p = re.compile(r"\d{5}")
    scrape()
