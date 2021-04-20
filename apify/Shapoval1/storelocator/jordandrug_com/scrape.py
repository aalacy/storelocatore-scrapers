import csv
import json
from lxml import html
from sgrequests import SgRequests
from concurrent import futures


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
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get("https://jordandrug.com/", headers=headers)
    tree = html.fromstring(r.text)
    return tree.xpath('//div[@class="col-xs-12 col-md-4"]/a/@href')


def get_data(url):
    locator_domain = "https://jordandrug.com"
    page_url = f"https://jordandrug.com{url}/locations"

    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }

    r = session.get(page_url, headers=headers)

    tree = html.fromstring(r.text)
    jsblock = "".join(tree.xpath('//script[@type="application/ld+json"]/text()'))
    js = json.loads(jsblock)

    street_address = js["@graph"][15]["address"]["streetAddress"]
    city = js["@graph"][15]["address"]["addressLocality"]
    state = js["@graph"][15]["address"]["addressRegion"]
    postal = js["@graph"][15]["address"]["postalCode"]
    country_code = "US"
    store_number = "<MISSING>"
    location_name = js["@graph"][15]["name"]
    phone = js["@graph"][15]["address"]["telephone"]
    latitude = js["@graph"][15]["geo"]["latitude"]
    longitude = js["@graph"][15]["geo"]["longitude"]
    location_type = js["@graph"][15]["@type"]
    hours = js["@graph"][15]["openingHoursSpecification"]
    tmp = []
    for h in hours:
        days = "".join(h.get("dayOfWeek")).split("/")[-1].strip()
        open = "".join(h.get("opens"))
        close = "".join(h.get("closes"))
        line = f"{days} {open} - {close}"
        if open == close:
            line = f"{days} - Closed"
        tmp.append(line)
    hours_of_operation = " ;".join(tmp)
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
