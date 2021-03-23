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
    locator_domain = "https://www.bonichoix.com/"
    api_url = "https://www.api-sobeys.com/magasins/stores_locator/MmE4ZTZiNjIzMWYzMzU2YTA4ZDBiZWIzNTdmMGQyOTA2ODk5YTNlNjQ3ZTBlMmM4NjVkYTA2YzU2NzA3Nzg1MmU0NGRhNjkwMWUwMjYyZThlZjMzZWU4YTRiM2E3OTVjMDk4ODUyZWE2MmIwNDEzZDQzN2VjMzU5ZmVlMDlkM2NLeDV0R2VORUhadENvME0wR25KWnZVcWhwMWRSTDc5WkJiaDlaMDBMVW9CMzRTc0VkVlpaRGZBbWU0RWNLTGVj/3?"

    session = SgRequests()
    r = session.get(api_url)
    js = r.json()

    for j in js:
        street_address = (
            f"{j.get('address')} {j.get('address2') or ''}".strip() or "<MISSING>"
        )
        city = j.get("city") or "<MISSING>"
        state = j.get("state") or "<MISSING>"
        postal = j.get("postal") or "<MISSING>"
        country_code = "CA"
        store_number = j.get("id") or "<MISSING>"
        page_url = f"https://www.bonichoix.com/en/store/{store_number}"
        location_name = j.get("name")
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
        try:
            starts = j.get("hours1").split(",")
            ends = j.get("hours2").split(",")
        except:
            starts, ends = list(), list()
        for d, s, e in zip(days, starts, ends):
            _tmp.append(f"{d}: {s} - {e}")

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
