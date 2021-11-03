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
    s = set()
    locator_domain = "https://yuzusushi.ca/"
    page_url = "https://yuzusushi.ca/en/locations"
    api_url = "https://yuzusushi.ca/api/store/stores"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0",
        "Accept": "application/json",
        "Accept-Language": "uk-UA,uk;q=0.8,en-US;q=0.5,en;q=0.3",
        "Connection": "keep-alive",
        "Referer": "https://yuzusushi.ca/en/locations",
        "TE": "Trailers",
    }
    session = SgRequests()
    r = session.get(api_url, headers=headers)
    js = r.json()

    for j in js:
        location_name = j.get("name")

        street_address = j.get("address")
        city = j.get("city") or "<MISSING>"
        state = j.get("provState") or "<MISSING>"
        postal = j.get("postalCode") or "<MISSING>"
        country_code = "CA"

        store_number = j.get("code") or "<MISSING>"
        if store_number in s:
            continue
        s.add(store_number)
        phone = j.get("phone") or "<MISSING>"
        latitude = j.get("latitude") or "<MISSING>"
        longitude = j.get("longitude") or "<MISSING>"
        if j.get("isExpress"):
            location_type = "Express"
        else:
            location_type = "Restaurant"

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
        hours = j.get("hours") or []
        for h in hours:
            day = days[h.get("day")]
            start = str(h.get("openingTime")).replace(".5", ":30")
            end = str(h.get("closingTime")).replace(".5", ":30")
            if start == end:
                _tmp.append(f"{day}: Closed")
            else:
                _tmp.append(f"{day}: {start} - {end}")

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
