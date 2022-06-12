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
    r = session.get(
        "https://www.enterprise.co.uk/en/car-hire/locations/uk.html?icid=footer.locations-_-uk.locations-_-ENGB.NULL"
    )
    tree = html.fromstring(r.text)
    sections = tree.xpath("//section[@class='band location-band region-list']")[1:]
    for s in sections:
        urls += s.xpath(".//a/@href")

    return urls


def get_data(page_url):
    locator_domain = "https://www.enterprise.co.uk/"

    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)
    text = "".join(
        tree.xpath(
            "//script[contains(text(), 'locationDetail.locationmap.locationId')]/text()"
        )
    )
    store_number = text.split("locationDetail.locationmap.locationId")[1].split('"')[1]
    api_url = f"https://prd-east.webapi.enterprise.co.uk/enterprise-ewt/location/{store_number}"
    r = session.get(api_url)
    j = r.json()["location"]

    location_name = j.get("name")
    a = j.get("address")
    street_address = ", ".join(a.get("street_addresses")).strip() or "<MISSING>"
    city = a.get("city") or "<MISSING>"
    state = "<MISSING>"
    postal = a.get("postal") or "<MISSING>"
    country_code = a.get("country_code")

    p = j.get("phones")
    if p:
        phone = f"{p[0].get('dialing_code')} {p[0].get('phone_number')}"
    else:
        phone = "<MISSING>"

    g = j.get("gps") or {}
    latitude = g.get("latitude") or "<MISSING>"
    longitude = g.get("longitude") or "<MISSING>"
    location_type = j.get("location_type") or "<MISSING>"

    _tmp = []
    try:
        days = j.get("hours")[0]["days"]
    except IndexError:
        days = []

    for d in days:
        day = d.get("day")
        start = d.get("open_close_times")[0].get("open_time")
        end = d.get("open_close_times")[0].get("close_time")

        if len(start) == 3:
            start = f"0{start}"

        if start != "0":
            _tmp.append(f"{day}: {start[:2]}:{start[2:]} - {end[:2]}:{end[2:]}")
        else:
            _tmp.append(f"{day}: Closed")

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
