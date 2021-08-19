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


def get_data(coords):
    rows = []
    locator_domain = "https://www.johnstonmurphy.com/"
    lat, lng = coords
    api_url = f"https://www.johnstonmurphy.com/on/demandware.store/Sites-johnston-murphy-us-Site/en_US/Stores-GetStoresByLatLong?distance=null&lat={lat}&long={lng}"

    session = SgRequests()
    r = session.get(api_url)
    js = r.json()["stores"]

    for j in js:
        location_name = j.get("name")
        street_address = (
            f"{j.get('address1')} {j.get('address2') or ''}".replace("null", "").strip()
            or "<MISSING>"
        )
        city = j.get("city") or "<MISSING>"
        state = j.get("stateCode") or "<MISSING>"
        postal = j.get("postalCode").replace("null", "") or "<MISSING>"
        country_code = j.get("countryCode") or "<MISSING>"
        if country_code == "United States":
            country_code = "US"
        elif country_code == "Canada":
            country_code = "CA"
        store_number = j.get("ID") or "<MISSING>"
        page_url = f"https://www.johnstonmurphy.com/on/demandware.store/Sites-johnston-murphy-us-Site/en_US/Stores-Details?StoreID={store_number}"
        phone = j.get("phone") or "<MISSING>"
        latitude = j.get("latitude") or "<MISSING>"
        longitude = j.get("longitude") or "<MISSING>"
        location_type = j.get("type") or "<MISSING>"
        if location_type not in {"Retail", "Factory"}:
            continue
        hours_of_operation = j.get("hours") or "<MISSING>"
        hours_of_operation = hours_of_operation.replace("\n", ";")
        if "closed" in hours_of_operation.lower() and "<" in hours_of_operation:
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

    countries = [SearchableCountries.USA, SearchableCountries.CANADA]
    for country in countries:
        coords = static_coordinate_list(radius=50, country_code=country)

        with futures.ThreadPoolExecutor(max_workers=5) as executor:
            future_to_url = {
                executor.submit(get_data, coord): coord for coord in coords
            }
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
