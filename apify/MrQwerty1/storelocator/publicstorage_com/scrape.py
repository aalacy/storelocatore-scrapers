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
    r = session.get("https://www.publicstorage.com/sitemap_plp.xml")
    tree = html.fromstring(r.content)

    return tree.xpath("//loc/text()")


def get_data(page_url):
    locator_domain = "https://www.publicstorage.com/"

    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)
    text = "".join(tree.xpath("//script[@type='application/ld+json']/text()"))
    j = json.loads(text)["@graph"][0]

    location_name = "".join(tree.xpath("//h1/text()")).strip()
    a = j.get("address")
    street_address = a.get("streetAddress") or "<MISSING>"
    city = a.get("addressLocality") or "<MISSING>"
    state = a.get("addressRegion") or "<MISSING>"
    postal = a.get("postalCode") or "<MISSING>"
    if len(postal) == 4:
        postal = f"0{postal}"
    country_code = a.get("addressCountry") or "<MISSING>"
    store_number = page_url.split("/")[-1]
    phone = j.get("telephone") or "<MISSING>"
    phone = phone.replace("+", "")
    g = j.get("geo") or {}
    latitude = g.get("latitude") or "<MISSING>"
    longitude = g.get("longitude") or "<MISSING>"
    location_type = "<MISSING>"

    _tmp = []
    hours = j.get("openingHoursSpecification") or []
    for h in hours:
        day = ",".join(h.get("dayOfWeek"))
        start = h.get("opens")
        end = h.get("closes")
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
    s = set()
    urls = get_urls()

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_data, url): url for url in urls}
        for future in futures.as_completed(future_to_url):
            row = future.result()
            if row:
                check = tuple(row[2:6])
                if check not in s:
                    s.add(check)
                    out.append(row)

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
