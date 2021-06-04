import csv

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


def fetch_data():
    out = []
    s = set()
    session = SgRequests()
    locator_domain = "https://www.hussle.com/"
    coords = static_coordinate_list(radius=50, country_code=SearchableCountries.BRITAIN)

    for coord in coords:
        lat, lng = coord
        for i in range(1, 57):
            api_url = f"https://public-api.hussle.com/search/gyms?filter[default][location_coords]={lat},{lng}&page[default][number]={i}&filter[default][location_distance]=50"
            r = session.get(api_url)
            js = r.json()["data"][0]["data"]["data"]

            for j in js:
                location_name = j.get("name")
                slug = j.get("b2c_gym_url")
                page_url = f"https://www.hussle.com{slug}"
                phone = j.get("telephone") or "<MISSING>"
                country_code = "GB"
                store_number = j.get("id") or "<MISSING>"
                location_type = "<MISSING>"

                a = j.get("location") or {}
                street_address = a.get("street_address") or "<MISSING>"
                city = a.get("locality") or "<MISSING>"
                state = "<MISSING>"
                postal = a.get("postcode") or "<MISSING>"
                latitude = a.get("latitude") or "<MISSING>"
                longitude = a.get("longitude") or "<MISSING>"

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
                hours = j.get("opening_times") or {}
                for d, t in zip(days, hours.values()):
                    start = t.get("opens_at")
                    close = t.get("closes_at")
                    _tmp.append(f"{d}: {start} - {close}")

                hours_of_operation = ";".join(_tmp) or "<MISSING>"

                if j.get("is_temporarily_closed"):
                    location_type = "Temporarily Closed"

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

                if store_number in s and store_number != "<MISSING>":
                    continue

                out.append(row)
                s.add(store_number)

            if len(js) < 18:
                break

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
