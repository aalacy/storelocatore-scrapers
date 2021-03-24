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
    locator_domain = "https://www.koodomobile.com/"
    lat, lng = coord
    api_url = f"https://www.koodomobile.com/koodo-store-locator/ajax/full?location={lat},{lng}&radius=50"
    page_url = "<MISSING>"

    session = SgRequests()
    r = session.get(api_url)
    js = r.json()["js_data"]["stores"].values()
    for j in js:
        location_name = j.get("name") or "<MISSING>"
        if "koodo" not in location_name.lower():
            continue

        street_address = j.get("address") or "<MISSING>"
        city = j.get("city") or "<MISSING>"
        state = j.get("province") or "<MISSING>"
        postal = j.get("postal_code") or "<MISSING>"
        country_code = "CA"
        if not j.get("address"):
            try:
                street_address = j.get("formatted_address").split(city)[0].strip()
                if "Beauport" in street_address:
                    street_address = street_address.split("Beauport")[0].strip()
                if street_address.endswith(","):
                    street_address = street_address[:-1]
            except:
                street_address = "<INACCESSIBLE>"

        store_number = j.get("store_id") or "<MISSING>"
        phone = j.get("phone_number") or "<MISSING>"
        latitude = j.get("latitude") or "<MISSING>"
        longitude = j.get("longitude") or "<MISSING>"
        location_type = "<MISSING>"

        _tmp = []
        days = [
            "MON",
            "TUE",
            "WED",
            "THU",
            "FRI",
            "SAT",
            "SUN",
        ]
        try:
            text = j.get("store_hours").split('"')

            for t in text:
                if "{" in t or "}" in t or ";" in t:
                    text.pop(text.index(t))

            for d in days:
                index = text.index(d)
                if index == len(text) - 1:
                    _tmp.append(f"{d}: Closed")
                else:
                    if ":" in text[index + 1]:
                        _tmp.append(f"{d}: {text[index + 1]}")
                    else:
                        _tmp.append(f"{d}: Closed")
        except:
            pass

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
        rows.append(row)

    return rows


def fetch_data():
    out = []
    s = set()
    coords = static_coordinate_list(radius=10, country_code=SearchableCountries.CANADA)

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
