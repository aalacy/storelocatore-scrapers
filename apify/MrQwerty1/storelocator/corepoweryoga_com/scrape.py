import csv

from concurrent import futures
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
    r = session.get("https://d7mth1zoj92fj.cloudfront.net/data/all-locations")
    js = r.json().values()
    for j in js:
        path = j.get("path")
        if path:
            urls.append(f"https://d7mth1zoj92fj.cloudfront.net/data/content{path}")

    return urls


def get_value(j, key, end_key="value"):
    try:
        value = j.get(key, {}).get("und", {}) or []
    except:
        return ""
    if value:
        return value[0].get(end_key)


def get_data(url):
    locator_domain = "https://www.corepoweryoga.com/"

    session = SgRequests()
    r = session.get(url)
    j = r.json()

    if str(j).lower().find("coming soon") != -1:
        return

    page_url = j.get("path") or "<MISSING>"
    location_name = j.get("title") or "<MISSING>"
    street_address = (
        f"{get_value(j, 'field_address_1')} {get_value(j, 'field_address_2') or ''}".strip()
        or "<MISSING>"
    )
    city = get_value(j, "field_city") or "<MISSING>"
    state = get_value(j, "field_studio_state") or "<MISSING>"
    postal = get_value(j, "field_zip_code") or "<MISSING>"
    country_code = get_value(j, "field_country") or "<MISSING>"
    if country_code == "USA" or country_code == "United States":
        country_code = "US"
    store_number = "<MISSING>"
    phone = get_value(j, "field_phone") or "<MISSING>"
    geo = get_value(j, "field_location", "geom")
    if geo:
        geo = geo.replace("POINT", "").replace("(", "").replace(")", "").strip().split()
        latitude = geo[1]
        longitude = geo[0]
    else:
        latitude = "<MISSING>"
        longitude = "<MISSING>"
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
    scrape()
