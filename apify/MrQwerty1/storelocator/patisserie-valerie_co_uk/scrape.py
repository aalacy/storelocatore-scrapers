import csv

from concurrent import futures
from sgrequests import SgRequests
from sgscrape.sgpostal import parse_address, International_Parser


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
    r = session.get(
        "https://www.closeby.co/embed/f312dbbc1e1036a6e7b395fbd18aaf1f/locations?cachable=true"
    )
    js = r.json()["locations"]
    for j in js:
        ids.append(j.get("id"))

    return ids


def get_data(store_number):
    locator_domain = "https://www.patisserie-valerie.co.uk/"
    page_url = "https://www.patisserie-valerie.co.uk/pages/patisserie-finder"
    api_url = f"https://www.closeby.co/locations/{store_number}"

    session = SgRequests()
    r = session.get(api_url)
    j = r.json()["location"]

    location_name = j.get("title")
    line = j.get("address_full")

    adr = parse_address(International_Parser(), line)
    street_address = (
        f"{adr.street_address_1} {adr.street_address_2 or ''}".replace(
            "None", ""
        ).strip()
        or "<MISSING>"
    )

    city = adr.city or "<MISSING>"
    state = adr.state or "<MISSING>"
    postal = adr.postcode or "<MISSING>"

    if location_name == "Kingston":
        city = street_address
        street_address = "<MISSING>"

    if city == "<MISSING>":
        city = location_name.split()[0]

    country_code = "GB"
    phone = j.get("phone_number") or "<MISSING>"
    latitude = j.get("latitude") or "<MISSING>"
    longitude = j.get("longitude") or "<MISSING>"
    location_type = "<MISSING>"

    _tmp = []
    hours = j.get("location_hours") or []
    for h in hours:
        day = h.get("day_full_name")
        start = h.get("time_open")
        close = h.get("time_close")
        _tmp.append(f"{day}: {start} - {close}")

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
    ids = get_ids()

    with futures.ThreadPoolExecutor(max_workers=2) as executor:
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
