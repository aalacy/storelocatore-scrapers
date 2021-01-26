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
    locator_domain = "https://www.tapiocaexpress.com/"
    api_url = "https://www.tapiocaexpress.com/wp-admin/admin-ajax.php"
    data = {"action": "csl_ajax_onload"}

    session = SgRequests()
    r = session.post(api_url, data=data)
    js = r.json()["response"]

    for j in js:
        street_address = (
            f"{j.get('address')} {j.get('address2') or ''}".strip() or "<MISSING>"
        )
        city = j.get("city") or "<MISSING>"
        state = j.get("state") or "<MISSING>"
        postal = j.get("zip") or "<MISSING>"
        if len(postal) == 4:
            postal = f"0{postal}"
        country_code = "US"
        store_number = j.get("id") or "<MISSING>"
        page_url = "https://www.tapiocaexpress.com/store-locator/"
        location_name = j.get("name")
        phone = j.get("phone") or "<MISSING>"
        latitude = j.get("lat") or "<MISSING>"
        longitude = j.get("lng") or "<MISSING>"
        location_type = "<MISSING>"
        hours = (
            j.get("hours")
            .replace("Store Hours", "")
            .replace("Store hours", "")
            .replace(": ", "")
            .strip()
        )
        hours_of_operation = hours or "<MISSING>"

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
