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
    locator_domain = "https://crosbysstores.com/"
    api_url = "https://crosbysstores.com/wp-admin/admin-ajax.php?action=asl_load_stores&load_all=1&layout=1"

    session = SgRequests()
    r = session.get(api_url)
    js = r.json()

    for j in js:

        street_address = j.get("street") or "<MISSING>"
        city = j.get("city") or "<MISSING>"
        state = j.get("state") or "<MISSING>"
        postal = j.get("postal_code") or "<MISSING>"
        country = j.get("country") or "<MISSING>"
        if country == "United States" or country == "USA":
            country_code = "US"
        else:
            country_code = country

        store_number = j.get("id") or "<MISSING>"
        page_url = j.get("website") or "<MISSING>"
        location_name = j.get("title")
        phone = j.get("phone") or "<MISSING>"
        latitude = j.get("lat") or "<MISSING>"
        longitude = j.get("lng") or "<MISSING>"
        location_type = "<MISSING>"
        text = j.get("open_hours") or ""
        jj = json.loads(text)
        hours_of_operation = (
            ";".join([f'{k}: {"".join(v)}' for k, v in jj.items()]) or "<MISSING>"
        )

        if hours_of_operation.count("1;") == 6:
            hours_of_operation = "Open 24 hours"

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
