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
    locator_domain = "https://www.timpson.co.uk/"
    lat, lon = coord

    session = SgRequests()
    data = {"start": "1000"}
    r = session.post(
        f"https://www.timpson.co.uk/storefinder/locator/get/{lat}/{lon}/", data=data
    )
    js = r.json()["locations"]

    for j in js:
        page_url = f'https://www.timpson.co.uk/stores/{j.get("url")}'
        location_name = j.get("name")
        street_address = j.get("street1") or "<MISSING>"
        city = j.get("city") or "<MISSING>"
        state = "<MISSING>"
        postal = j.get("zip") or "<MISSING>"
        country_code = "GB"
        store_number = j.get("store_no") or "<MISSING>"
        phone = j.get("phone") or "<MISSING>"
        latitude = j.get("lat") or "<MISSING>"
        longitude = j.get("lng") or "<MISSING>"
        location_type = "<MISSING>"

        _tmp = []
        days = [
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday",
        ]

        for i in range(1, 8):
            time = j.get(f"opening_{i}")
            day = days[i - 1]
            _tmp.append(f"{day}: {time}")

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
    coords = static_coordinate_list(
        radius=200, country_code=SearchableCountries.BRITAIN
    )

    with futures.ThreadPoolExecutor(max_workers=20) as executor:
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
