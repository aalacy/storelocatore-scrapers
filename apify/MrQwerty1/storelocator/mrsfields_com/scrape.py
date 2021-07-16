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
    r = session.get("https://www.mrsfields.com/stores/")
    tree = html.fromstring(r.text)

    return tree.xpath("//div[@class='state-list']//a/@href")


def get_data(url):
    rows = []

    locator_domain = "https://www.mrsfields.com"
    api_url = f"{locator_domain}{url}"

    session = SgRequests()
    r = session.get(api_url)
    tree = html.fromstring(r.text)
    text = "".join(tree.xpath("//script[contains(text(), 'var data =')]/text()"))
    text = text.split("var data = { data:")[1].split(" }")[0]
    js = json.loads(text)

    for j in js:
        location_name = j.get("name").strip()

        adr1 = j.get("address1")
        adr2 = j.get("address2") or ""
        street_address = f"{adr1} {adr2}".strip() or "<MISSING>"
        if "events" in adr1.lower() and adr2:
            street_address = adr2
        elif "events" in adr1.lower() and not adr2:
            street_address = adr1.split("EVENTS")[-1]
        if "events" in adr2.lower():
            street_address = adr1
        city = j.get("city") or "<MISSING>"
        state = j.get("state") or "<MISSING>"
        postal = j.get("zip") or "<MISSING>"
        country_code = "US"
        store_number = j.get("store_num") or "<MISSING>"
        slug = j.get("store_url") or ""
        page_url = "<MISSING>"
        if slug:
            page_url = f"https://www.mrsfields.com{slug}"

        phone = j.get("phone") or "<MISSING>"
        if phone == "0000000000":
            phone = "<MISSING>"
        latitude = j.get("lat") or "<MISSING>"
        longitude = j.get("lng") or "<MISSING>"
        location_type = "<MISSING>"
        hours_of_operation = j.get("store_hours") or "<MISSING>"

        status = j.get("store_status") or ""
        if "temp" in status:
            hours_of_operation = "Temporarily Closed"
        elif "coming" in status:
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
            hours_of_operation.replace("\n", ";"),
        ]

        rows.append(row)

    return rows


def fetch_data():
    out = []
    s = set()
    urls = get_urls()

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_data, url): url for url in urls}
        for future in futures.as_completed(future_to_url):
            rows = future.result()
            for row in rows:
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
