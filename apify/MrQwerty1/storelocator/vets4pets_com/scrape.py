import csv
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


def fetch_data():
    out = []
    locator_domain = "https://www.vets4pets.com/"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:84.0) Gecko/20100101 Firefox/84.0",
        "Accept": "*/*",
        "Accept-Language": "uk-UA,uk;q=0.8,en-US;q=0.5,en;q=0.3",
        "Referer": "https://www.vets4pets.com/find-a-practice/",
        "Origin": "https://www.vets4pets.com",
        "Connection": "keep-alive",
        "TE": "Trailers",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
    }

    params = (
        ("key", "woos-85314341-5e66-3ddf-bb9a-43b1ce46dbdc"),
        ("lat", "51.50732"),
        ("lng", "-0.12764746"),
        ("max_distance", "50000"),
        ("stores_by_page", "250"),
        ("limit", "1000"),
        ("page", "1"),
    )

    session = SgRequests()
    r = session.get(
        "https://api.woosmap.com/stores/search", headers=headers, params=params
    )
    js = r.json()["features"]

    for j in js:
        g = j.get("geometry")
        j = j.get("properties")
        c = j.get("contact")
        a = j.get("address")
        street_address = (
            ", ".join(a.get("lines")).replace("Inside Pets at Home,", "").strip()
            or "<MISSING>"
        )
        city = a.get("city") or "<MISSING>"
        state = "<MISSING>"
        postal = a.get("zipcode") or "<MISSING>"
        country_code = a.get("country_code") or "<MISSING>"
        store_number = j.get("store_id") or "<MISSING>"
        page_url = c.get("website") or "<MISSING>"
        location_name = j.get("name")
        phone = c.get("phone") or "<MISSING>"
        longitude, latitude = g.get("coordinates") or ["<MISSING>", "<MISSING>"]
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
        hours = j.get("opening_hours").get("usual")
        for k, v in hours.items():
            day = days[int(k) - 1]
            start = v[0].get("start")
            close = v[0].get("end")
            _tmp.append(f"{day}: {start} - {close}")

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
        out.append(row)

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
