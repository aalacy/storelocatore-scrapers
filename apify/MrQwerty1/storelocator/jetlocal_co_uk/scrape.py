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
    locator_domain = "https://www.jetlocal.co.uk/"
    api_url = "https://storerocket.global.ssl.fastly.net/api/user/2BkJ1wEpqR/locations?filters=3202"

    session = SgRequests()
    r = session.get(api_url)
    js = r.json()["results"]["locations"]

    for j in js:
        street_address = (
            f"{j.get('address_line_1')} {j.get('address_line_2') or ''}".strip()
            or "<MISSING>"
        )
        city = j.get("state") or "<MISSING>"
        state = "<MISSING>"
        postal = j.get("postcode") or "<MISSING>"
        country_code = j.get("country") or "<MISSING>"
        store_number = "<MISSING>"
        page_url = j.get("url") or "https://www.jetlocal.co.uk/drivers/locator"
        location_name = j.get("name")
        phone = "<MISSING>"
        latitude = j.get("lat") or "<MISSING>"
        longitude = j.get("lng") or "<MISSING>"
        location_type = "<MISSING>"

        _tmp = []
        hours = j.get("hours")
        for k, v in hours.items():
            if not v:
                continue
            _tmp.append(f"{k.capitalize()}: {v}")

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

        check = tuple(row[2:6])
        if check in s:
            continue

        s.add(check)
        out.append(row)

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
