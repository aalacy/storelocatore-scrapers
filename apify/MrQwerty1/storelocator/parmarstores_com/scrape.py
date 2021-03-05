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


def get_ids():
    ids = set()
    session = SgRequests()
    r = session.get(
        "https://www.parmarstores.com/wp-json/store-locator-plus/v2/locations/"
    )
    js = r.json()
    for j in js:
        ids.add(j["sl_id"])

    return ids


def get_data(_id):
    locator_domain = "https://www.parmarstores.com/"
    api_url = (
        f"https://www.parmarstores.com/wp-json/store-locator-plus/v2/locations/{_id}"
    )

    session = SgRequests()
    r = session.get(api_url)
    j = r.json()

    page_url = "<MISSING>"
    location_name = j.get("sl_store").strip()
    street_address = (
        f"{j.get('sl_address')} {j.get('sl_address2') or ''}".strip() or "<MISSING>"
    )
    city = j.get("sl_city") or "<MISSING>"
    state = j.get("sl_state") or "<MISSING>"
    postal = j.get("sl_zip") or "<MISSING>"
    country_code = j.get("sl_country") or "US"
    if country_code == "USA" or country_code == "United States":
        country_code = "US"
    store_number = location_name.split("#")[-1].strip()
    phone = j.get("sl_phone") or "<MISSING>"
    latitude = j.get("sl_latitude") or "<MISSING>"
    longitude = j.get("sl_longitude") or "<MISSING>"
    location_type = "<MISSING>"
    hours_of_operation = (
        j.get("sl_hours")
        .replace("strong", "")
        .replace("<", "")
        .replace(">", "")
        .replace("/", "")
        .replace("\r\n", ";")
        or "<MISSING>"
    )

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
    ids = get_ids()

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_data, _id): _id for _id in ids}
        for future in futures.as_completed(future_to_url):
            row = future.result()
            if row:
                _id = row[8]
                if _id not in s:
                    s.add(_id)
                    out.append(row)

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
