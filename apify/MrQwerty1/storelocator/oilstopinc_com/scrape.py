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


def clean_phone(text):
    out = []
    if text.find("|") != -1:
        text = text.split("|")[0].strip()

    for t in text:
        if t.isdigit():
            out.append(t)

    return "(" + "".join(out[:3]) + ") " + "".join(out[3:6]) + "-" + "".join(out[6:])


def get_urls():
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0"
    }
    r = session.get("https://oilstopinc.com/locations/", headers=headers)
    tree = html.fromstring(r.text)

    return tree.xpath("//a[@class='locations-table']/@href")


def get_data(page_url):
    locator_domain = "https://oilstopinc.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0"
    }
    if page_url.find("oil") == -1:
        return
    if page_url.startswith("/"):
        page_url = f"https://oilstopinc.com{page_url}"

    session = SgRequests()
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)

    location_name = "".join(tree.xpath("//h1/text()")).replace("\n", "").strip()
    line = tree.xpath("//*[@class='tlocations']//text()")
    line = list(filter(None, [l.strip() for l in line]))
    street_address = "<MISSING>"
    phone = "<MISSING>"
    part = ""
    hours = ""
    for l in line:
        if (
            l[0].isdigit()
            and l.find("reviews") == -1
            and not re.findall(r"(\d{3}-\d{4})", l)
        ):
            street_address = l
        if re.findall(r"(\d{3}-\d{4})", l):
            phone = clean_phone(l)
        if re.findall(r"\d{5}", l):
            part = l
        if l.find("Open") != -1:
            hours = l.replace("Open", "").replace(" / ", ";").replace(", ", ";").strip()
            if hours.find("|") != -1:
                hours = hours.split("|")[-1].strip()

    city = part.split(",")[0].strip()
    part = part.split(",")[1].strip()
    state = part.split()[0]
    postal = part.split()[1]
    country_code = "US"
    store_number = "<MISSING>"
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    location_type = "<MISSING>"
    hours_of_operation = hours or "<MISSING>"

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
