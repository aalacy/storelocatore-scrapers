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
    ids = []
    session = SgRequests()
    r = session.get("https://www.crunchfitness.ca/crunch_core/clubs")
    js = r.json()
    for j in js:
        ids.append(j["id"])

    return ids


def get_data(_id):
    locator_domain = "https://crunchfitness.ca/"
    api_url = f"https://www.crunchfitness.ca/crunch_core/clubs/{_id}"

    session = SgRequests()
    r = session.get(api_url)
    j = r.json()

    page_url = f'https://www.crunchfitness.ca/locations/{j.get("slug")}'
    location_name = j.get("name").strip()
    a = j.get("address", {})
    street_address = (
        f"{a.get('address_1')} {a.get('address_2') or ''}".strip() or "<MISSING>"
    )
    city = a.get("city") or "<MISSING>"
    state = a.get("state") or "<MISSING>"
    postal = a.get("zip") or "<MISSING>"
    country_code = a.get("country_code") or "<MISSING>"
    store_number = _id
    phone = j.get("phone")
    latitude = j.get("latitude") or "<MISSING>"
    longitude = j.get("longitude") or "<MISSING>"
    location_type = "<MISSING>"
    hours_of_operation = j.get("hours").replace("\n", ";") or "<MISSING>"
    status = j.get("status") or ""

    if status.find("coming") != -1:
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
    ids = get_ids()

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_data, _id): _id for _id in ids}
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
