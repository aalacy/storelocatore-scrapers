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
    url = "https://nekterjuicebar.com"
    api_url = "https://locations.nekterjuicebar.com/modules/multilocation/?near_location=75022&threshold=5000&published=1&within_business=true&limit=1000"

    session = SgRequests()
    r = session.get(api_url)
    js = r.json()["objects"]

    for j in js:
        locator_domain = url
        street_address = (
            f"{j.get('street')} {j.get('street2') or ''}".strip() or "<MISSING>"
        )
        city = j.get("city") or "<MISSING>"
        state = j.get("state") or "<MISSING>"
        postal = j.get("postal_code") or "<MISSING>"
        country_code = j.get("country") or "<MISSING>"
        store_number = j.get("partner_location_id") or "<MISSING>"
        page_url = j.get("homepage_url") or "<MISSING>"
        location_name = j.get("location_name")
        phone = j.get("phones")[0].get("number") if j.get("phones") else "<MISSING>"
        latitude = j.get("lat") or "<MISSING>"
        longitude = j.get("lon") or "<MISSING>"
        location_type = "<MISSING>"

        _tmp = []
        hours = j.get("formatted_hours", {}).get("primary", {}).get("days") or []
        for h in hours:
            day = h.get("label")
            time = h.get("content")
            _tmp.append(f"{day}: {time}")

        hours_of_operation = ";".join(_tmp) or "<MISSING>"

        if hours_of_operation.count("Closed") == 7:
            hours_of_operation = "Closed"

        if phone[0] != "(" and phone != "<MISSING>":
            phone = "<MISSING>"
            hours_of_operation = "Coming Soon"

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
