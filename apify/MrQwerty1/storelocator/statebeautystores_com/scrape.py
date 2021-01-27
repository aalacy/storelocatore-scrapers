import csv
import re

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


def clean_phone(text):
    regex = r"\d{3}-\d{3}-\d{4}"
    phone = re.findall(regex, text)
    if phone:
        return phone[0]
    return "<MISSING>"


def get_data(coord):
    rows = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:83.0) Gecko/20100101 Firefox/83.0"
    }
    lat, lon = coord
    locator_domain = "https://statebeautystores.com/"
    api_url = f"https://www.state-rda.com/wp-admin/admin-ajax.php?action=store_search&lat={lat}&lng={lon}&max_results=100&search_radius=200"

    session = SgRequests()
    r = session.get(api_url, headers=headers)
    js = r.json()

    for j in js:
        page_url = "https://www.state-rda.com/store-locator/"
        location_name = j.get("store").replace("\t", " ").strip()
        street_address = (
            f"{j.get('address')} {j.get('address2') or ''}".strip() or "<MISSING>"
        )

        if street_address.find("(") != -1:
            street_address = street_address.split("(")[0].strip()
        city = j.get("city") or "<MISSING>"
        state = j.get("state") or "<MISSING>"
        if state == "Albuquerque":
            city = "Albuquerque"
            state = "NM"

        if state == "TNB":
            state = "TN"

        postal = j.get("zip") or "<MISSING>"
        country = j.get("country") or "<MISSING>"
        if country == "United States" or country == "USA":
            country_code = "US"
        else:
            country_code = "<MISSING>"
        store_number = j.get("id") or "<MISSING>"
        phone = clean_phone(j.get("phone"))

        latitude = j.get("lat") or "<MISSING>"
        longitude = j.get("lng") or "<MISSING>"

        if location_name.find("RDA") != -1:
            location_type = "RDA Pro Mart"
        else:
            location_type = "State Beauty Supply"

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
