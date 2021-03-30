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


def get_ids():
    session = SgRequests()
    r = session.get("https://www.laborfinders.com/locations/")
    tree = html.fromstring(r.text)

    return tree.xpath("//a[@class='small blue']/@data-set-location")


def get_data(_id):
    locator_domain = "https://www.laborfinders.com/"
    api_url = f"https://www.laborfinders.com/umbraco/surface/ExamineSearchSurface/SetLocation?location={_id}"

    session = SgRequests()
    r = session.get(api_url)
    j = r.json()

    location_name = j.get("Name").strip()
    street_address = (
        f"{j.get('Address1')} {j.get('Address2') or ''}".strip() or "<MISSING>"
    )
    city = j.get("City") or "<MISSING>"
    state = j.get("State") or "<MISSING>"
    postal = j.get("PostalCode") or "<MISSING>"
    country_code = "US"
    page_url = f'https://www.laborfinders.com/locations/{state}/{city}/{_id.replace(", ", "-")}/'
    store_number = "<MISSING>"
    phone = j.get("Phone") or "<MISSING>"
    geo = j.get("Coordinates", {}) or {}
    latitude = geo.get("Latitude") or "<MISSING>"
    longitude = geo.get("Longitude") or "<MISSING>"
    location_type = "<MISSING>"

    _tmp = []
    days = [
        "Sunday",
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
    ]
    hours = j.get("Hours") or []

    i = 0
    for h in hours:
        if h["Open"]["IsClosed"]:
            _tmp.append(f"{days[i]}: Closed")
        else:
            start = h["Open"]["AMPM"]
            end = h["Close"]["AMPM"]
            _tmp.append(f"{days[i]}: {start} - {end}")
        i += 1

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
