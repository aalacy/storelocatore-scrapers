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
    session = SgRequests()
    r = session.get(
        "https://davpartcorp.mallmaverick.com/api/v4/davpartcorp/child_properties.json"
    )

    return r.json()["categories"]["retail"]


def get_data(slug):
    locator_domain = "https://davpart.com/"
    api = f"https://davpartcorp.mallmaverick.com/api/v4/{slug}/all.json"
    page_url = f"https://davpart.com/retail/{slug}"

    session = SgRequests()
    r = session.get(api)
    j = r.json()["property"]

    location_name = j.get("name")
    street_address = f'{j.get("address1")} {j.get("address2") or ""}'.strip()
    city = j.get("city") or "<MISSING>"
    state = j.get("province_state") or "<MISSING>"
    postal = j.get("postal_code") or "<MISSING>"
    country_code = "CA"
    if len(postal) == 5:
        country_code = "US"
    store_number = "<MISSING>"
    phone = j.get("contact_phone") or "<MISSING>"
    latitude = j.get("latitude") or "<MISSING>"
    longitude = j.get("longitude") or "<MISSING>"
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
