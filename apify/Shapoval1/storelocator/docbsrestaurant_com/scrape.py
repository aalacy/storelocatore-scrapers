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

    locator_domain = "https://docbsrestaurant.com"
    api_url = "https://docbsrestaurant.com/page-data/sq/d/1778102472.json"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()["data"]["allLocation"]["edges"]

    for j in js:
        a = j.get("node")
        slug = a.get("slug")
        page_url = f"https://docbsrestaurant.com/locations/{slug}"

        location_name = a.get("name")
        location_type = "Restaurant"
        street_address = f"{a.get('address')} {a.get('address2') or ''}".strip()
        phone = a.get("phone")
        state = a.get("state")
        postal = a.get("zip")
        country_code = "US"
        city = a.get("city")
        store_number = a.get("store")
        latitude = a.get("latitude")
        longitude = a.get("longitude")
        hours = a.get("hours")[0].get("hours")
        tmp = []
        for h in hours:
            day = h.get("days")
            times = h.get("times")
            line = f"{day} {times}"
            tmp.append(line)

        hours_of_operation = "; ".join(tmp) or "<MISSING>"

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
