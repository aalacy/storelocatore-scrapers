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
    locator_domain = "http://www.gristedessupermarkets.com/"
    page_url = "http://www.gristedessupermarkets.com/store-locator/"
    api_url = "http://www.gristedessupermarkets.com/wp-admin/admin-ajax.php"
    data = {"lat": "37.09024", "lng": "-95.712891", "action": "csl_ajax_onload"}

    session = SgRequests()
    r = session.post(api_url, data=data)
    js = r.json()["response"]

    for j in js:
        street_address = (
            f"{j.get('address')} {j.get('address2') or ''}".replace(
                "&amp;", "&"
            ).strip()
            or "<MISSING>"
        )
        city = j.get("city") or "<MISSING>"
        state = j.get("state") or "<MISSING>"
        postal = j.get("zip") or "<MISSING>"
        country_code = "US"
        location_name = j.get("name")
        if location_name.find("(") != -1:
            location_name = location_name.split("(")[0].strip()
        store_number = location_name.replace("Store ", "")
        phone = j.get("phone") or "<MISSING>"
        if phone.find("/") != -1:
            phone = phone.split("/")[0].strip()
        latitude = j.get("lat") or "<MISSING>"
        longitude = j.get("lng") or "<MISSING>"
        location_type = "<MISSING>"
        hours_of_operation = j.get("hours") or "<MISSING>"
        hours_of_operation = hours_of_operation.replace("\r\n", ";")

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
