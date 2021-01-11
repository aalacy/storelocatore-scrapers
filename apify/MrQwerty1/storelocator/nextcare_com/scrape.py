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


def get_dicts():
    out = []
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:84.0) Gecko/20100101 Firefox/84.0"
    }
    r = session.get("https://nextcare.com/locations/az/", headers=headers)
    tree = html.fromstring(r.text)
    text = (
        "".join(tree.xpath("//script[contains(text(), 'var nextcareObject')]/text()"))
        .split('"locations_data":')[1]
        .split("};")[0]
    )
    js = json.loads(text)

    for j in js:
        out.append(j)

    return out


def get_data(d):
    locator_domain = "https://nextcare.com/"
    _id = d.get("post_id")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:84.0) Gecko/20100101 Firefox/84.0"
    }
    api_url = f"https://nextcare.com/?p={_id}"

    session = SgRequests()
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)

    page_url = r.url
    location_name = d.get("title")
    street_address = (
        f"{d.get('street')} {d.get('aptsuit') or ''}".strip() or "<MISSING>"
    )
    city = d.get("city") or "<MISSING>"
    state = d.get("state") or "<MISSING>"
    postal = d.get("zipcode") or "<MISSING>"
    country_code = d.get("country") or "<MISSING>"
    store_number = _id
    try:
        phone = tree.xpath("//li[@class='tel-list']/a/text()")[0].strip()
    except:
        phone = "<MISSING>"
    latitude = d.get("lat") or "<MISSING>"
    longitude = d.get("lng") or "<MISSING>"
    location_type = "<MISSING>"

    _tmp = []
    li = tree.xpath("//ul[@class='day-list']/li")
    for l in li:
        day = "".join(l.xpath("./span[1]/text()"))
        time = "".join(l.xpath("./span[2]/text()"))
        _tmp.append(f"{day}: {time}")

    hours_of_operation = ";".join(_tmp) or "<MISSING>"

    if location_name.lower().find("coming soon") != -1:
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
    dicts = get_dicts()

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_data, d): d for d in dicts}
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
