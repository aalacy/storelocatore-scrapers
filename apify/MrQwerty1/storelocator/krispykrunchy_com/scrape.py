import csv

from concurrent import futures
from sgrequests import SgRequests
from sgzip.static import static_coordinate_list, SearchableCountries


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


def get_data(coord):
    rows = []
    lat, lon = coord
    locator_domain = "https://krispykrunchy.com/"
    api_url = f"https://krispykrunchy.com/wp-admin/admin-ajax.php?action=store_search&lat={lat}&lng={lon}&max_results=100&search_radius=50&autoload=1"

    session = SgRequests()
    r = session.get(api_url)
    js = r.json()

    for j in js:
        page_url = j.get("permalink") or "<MISSING>"
        location_name = (
            j.get("store")
            .replace("&#8217;", "'")
            .replace("&#038;", "&")
            .replace("&#8211;", "-")
            .strip()
        )
        street_address = (
            f"{j.get('address')} {j.get('address2') or ''}".strip() or "<MISSING>"
        )
        city = j.get("city") or "<MISSING>"
        state = j.get("state") or "<MISSING>"
        if len(state) > 2 and state != "<MISSING>":
            continue
        postal = j.get("zip") or "<MISSING>"
        country_code = "US"
        store_number = j.get("id") or "<MISSING>"
        phone = j.get("phone") or "<MISSING>"
        latitude = j.get("lat") or "<MISSING>"
        longitude = j.get("lng") or "<MISSING>"
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

        rows.append(row)

    return rows


def fetch_data():
    out = []
    s = set()
    coords = static_coordinate_list(radius=50, country_code=SearchableCountries.USA)

    with futures.ThreadPoolExecutor(max_workers=2) as executor:
        future_to_url = {executor.submit(get_data, coord): coord for coord in coords}
        for future in futures.as_completed(future_to_url):
            rows = future.result()
            for row in rows:
                _id = tuple(row[2:6])
                if _id not in s:
                    s.add(_id)
                    out.append(row)

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
