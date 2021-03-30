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
    headers = {
        "authority": "www.libertymutual.com",
        "adrum": "isAjax:true",
        "user-agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36 OPR/72.0.3815.400",
        "accept": "*/*",
        "sec-fetch-site": "same-origin",
        "sec-fetch-mode": "cors",
        "sec-fetch-dest": "empty",
        "accept-language": "uk-UA,uk;q=0.9,en-US;q=0.8,en;q=0.7",
    }

    locator_domain = "https://www.libertymutual.com/"
    api_url = f"https://www.libertymutual.com/api/v2/entity/officesearch?longitude={lon}&latitude={lat}&searchRadius=200&busofficetype=Sales"

    session = SgRequests()
    r = session.get(api_url, headers=headers)
    js = r.json().get("data") or []

    for j in js:
        page_url = f'https://www.libertymutual.com/office/{j.get("queryValue")}'
        location_name = j.get("name").strip()
        a = j.get("address", {}) or {}
        street_address = (
            f"{a.get('street')} {a.get('additionalStreetInfo') or ''}".strip()
            or "<MISSING>"
        )
        city = a.get("city") or "<MISSING>"
        state = a.get("state", {}).get("code") or "<MISSING>"
        postal = a.get("zip") or "<MISSING>"
        country_code = "US"
        store_number = j.get("officeCode") or "<MISSING>"
        phone = j.get("phones", {}).get("primary", {}).get("number") or "<MISSING>"
        loc = j.get("location", {}).get("coordinates", ["<MISSING>", "<MISSING>"]) or [
            "<MISSING>",
            "<MISSING>",
        ]
        latitude = loc[1] or "<MISSING>"
        longitude = loc[0] or "<MISSING>"
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
    coords = static_coordinate_list(radius=200, country_code=SearchableCountries.USA)

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_data, coord): coord for coord in coords}
        for future in futures.as_completed(future_to_url):
            rows = future.result()
            for row in rows:
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
