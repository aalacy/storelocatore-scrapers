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
    locator_domain = "https://www.decathlon.co.uk/"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:84.0) Gecko/20100101 Firefox/84.0",
        "Accept": "*/*",
        "Accept-Language": "uk-UA,uk;q=0.8,en-US;q=0.5,en;q=0.3",
        "Origin": "https://www.decathlon.co.uk",
        "Connection": "keep-alive",
        "Referer": "https://www.decathlon.co.uk/store-locator",
        "TE": "Trailers",
    }

    session = SgRequests()
    r = session.get(
        "https://api.woosmap.com/stores/search/?key=woos-4c9860ae-4147-39e0-af88-6d56fc1a5ab6&lat=51.50732&lng=-0.12764746&stores_by_page=200",
        headers=headers,
    )

    js = r.json()["features"]

    for j in js:
        g = j.get("geometry")
        j = j.get("properties")
        c = j.get("contact")
        a = j.get("address")
        street_address = a.get("lines") or []
        street_address = list(filter(None, street_address))
        street_address = ", ".join(street_address) or "<MISSING>"
        city = a.get("city") or "<MISSING>"
        state = "<MISSING>"
        postal = a.get("zipcode") or "<MISSING>"
        country_code = a.get("country_code") or "<MISSING>"
        store_number = j.get("store_id") or "<MISSING>"
        page_url = f"https://www.decathlon.co.uk/store-view/-{store_number}"
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
            if v:
                start = v[0].get("start")
                close = v[0].get("end")
                _tmp.append(f"{day}: {start} - {close}")
            else:
                _tmp.append(f"{day}: Closed")

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
        out.append(row)

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
