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
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:84.0) Gecko/20100101 Firefox/84.0"
    }

    locator_domain = "https://www.moes.com/"
    api_url = f"https://www.moes.com/sitecore/api/v0.1/storelocator/locations?lat={lat}&lng={lon}"

    session = SgRequests()
    r = session.get(api_url, headers=headers)
    js = r.json()["Locations"]

    for j in js:
        page_url = "https://www.moes.com" + j.get("Url")
        location_name = j.get("LocationName").strip()
        street_address = j.get("StreetAddress") or "<MISSING>"
        city = j.get("City") or "<MISSING>"
        state = j.get("Region") or "<MISSING>"
        postal = j.get("PostalCode") or "<MISSING>"
        country_code = j.get("CountryName") or "<MISSING>"
        if country_code == "GU":
            continue

        store_number = j.get("StoreNumber") or "<MISSING>"
        phone = j.get("Phone") or "<MISSING>"
        latitude = j.get("Latitude") or "<MISSING>"
        longitude = j.get("Longitude") or "<MISSING>"
        location_type = "<MISSING>"

        _tmp = []
        hours = j.get("Hours", [])

        for h in hours:
            day = h.get("FormattedDayOfWeek")
            if day == "today":
                continue

            start = h.get("Open")
            close = h.get("Close")
            if start == close:
                _tmp.append(f"{day}: Closed")
            else:
                _tmp.append(f"{day}: {start} - {close}")

        hours_of_operation = ";".join(_tmp) or "<MISSING>"

        if hours_of_operation.count("Closed") == 7:
            hours_of_operation = "Closed"

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
    coords = static_coordinate_list(radius=100, country_code=SearchableCountries.USA)

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
