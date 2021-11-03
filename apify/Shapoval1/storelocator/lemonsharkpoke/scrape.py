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

    locator_domain = "https://lemonsharkpoke.com"

    api_url = "https://lemonsharkpoke.com/wp-admin/admin-ajax.php?action=asl_load_stores&nonce=e2fd3ecab0&load_all=1&layout=1"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()
    for j in js:

        page_url = j.get("website") or "https://lemonsharkpoke.com/locations/"
        location_name = "".join(j.get("title")).strip()
        location_type = "<MISSING>"
        street_address = "".join(j.get("street"))
        phone = j.get("phone") or "<MISSING>"
        latitude = j.get("lat")
        longitude = j.get("lng")
        country_code = j.get("country")
        state = j.get("state")
        postal = j.get("postal_code")
        city = j.get("city")
        store_number = "<MISSING>"
        hours_of_operation = (
            "".join(j.get("open_hours"))
            .replace("{", "")
            .replace('"', "")
            .replace("[", "")
            .replace("]", "")
            .replace("}", "")
        )

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
