import csv
import json

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
    url = "https://www.greasemonkeyauto.com/"
    api_url = "https://www.greasemonkeyauto.com/wp-admin/admin-ajax.php?action=asl_load_stores&load_all=1&layout=1&category=87%2C86%2C85%2C84%2C83%2C82%2C81%2C80%2C79%2C78%2C77%2C76%2C75%2C74%2C73%2C72%2C71%2C70%2C69%2C68%2C67%2C66%2C65%2C64%2C63%2C62%2C61%2C60%2C58%2C57%2C56%2C55%2C53%2C132%2C143"

    session = SgRequests()
    r = session.get(api_url)
    js = r.json()

    for j in js:
        locator_domain = url
        location_name = j.get("title") or "<MISSING>"
        street_address = j.get("street") or "<MISSING>"
        city = j.get("city") or "<MISSING>"
        state = j.get("state") or "<MISSING>"
        postal = j.get("postal_code") or "<MISSING>"
        country_code = "US"
        store_number = j.get("id") or "<MISSING>"
        page_url = j.get("website") or "<MISSING>"
        phone = j.get("phone") or "<MISSING>"
        latitude = j.get("lat") or "<MISSING>"
        longitude = j.get("lng") or "<MISSING>"
        location_type = "<MISSING>"

        _tmp = []
        hours = j.get("open_hours") or ""
        hours = json.loads(hours)

        for k, v in hours.items():
            if v == "0":
                _tmp.append(f"{k.capitalize()}: Closed")
            else:
                _tmp.append(f"{k.capitalize()}: {v[0]}")

        hours_of_operation = ";".join(_tmp) or "<MISSING>"

        if hours_of_operation.count("Closed") == 7:
            hours_of_operation = "<INACCESSIBLE>"

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
