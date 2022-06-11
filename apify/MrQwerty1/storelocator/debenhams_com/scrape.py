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
    locator_domain = "https://debenhams.com/"
    lat, lon = coord
    api_url = f"https://mystore.debenhams.com/data/search.json?&lat={lat}&lng={lon}"
    page_url = "<MISSING>"

    session = SgRequests()
    r = session.get(api_url)
    js = r.json()

    for j in js:
        location_name = j.get("name")
        street_address = f"{j.get('addr1')} {j.get('addr2') or ''}" or "<MISSING>"
        city = j.get("city") or "<MISSING>"
        state = j.get("state") or "<MISSING>"
        postal = j.get("postcode") or "<MISSING>"
        country_code = j.get("countrycode") or "<MISSING>"
        if country_code != "GB":
            continue
        store_number = j.get("number") or "<MISSING>"
        phone = j.get("phone") or "<MISSING>"
        latitude = j.get("lat") or "<MISSING>"
        longitude = j.get("lon") or "<MISSING>"
        location_type = "<MISSING>"

        _tmp = []
        days = [
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Friday",
        ]
        for i in range(1, 8):
            day = days[i - 1]
            time = j.get(f"o{i}")
            _tmp.append(f"{day}: {time}")

        hours_of_operation = ";".join(_tmp) or "<MISSING>"
        if hours_of_operation.lower().count("temp") == 7:
            hours_of_operation = "Temporarily Closed"

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
    coords = static_coordinate_list(radius=10, country_code=SearchableCountries.BRITAIN)

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
