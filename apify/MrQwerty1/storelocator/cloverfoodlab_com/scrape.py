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
    locator_domain = "https://www.cloverfoodlab.com/"
    api_url = "https://menu.cloverfoodlab.com/api/locations"

    session = SgRequests()
    r = session.get(api_url)
    js = r.json()["locations"]

    for j in js:
        if j.get("is_internal"):
            continue
        street_address = (
            f"{j.get('address_street_1')} {j.get('address_street_2') or ''}".strip()
            or "<MISSING>"
        )
        if "None" in street_address or "Twitter" in street_address:
            street_address = "<MISSING>"
        city = j.get("address_city") or "<MISSING>"
        state = j.get("address_state") or "<MISSING>"
        postal = j.get("address_zip_code") or "<MISSING>"
        country_code = "US"
        store_number = j.get("id") or "<MISSING>"
        page_url = (
            f'https://www.cloverfoodlab.com/locations/location/?l={j.get("slug")}'
        )
        location_name = j.get("description")
        if "(" in location_name:
            location_name = location_name.split("(")[0].strip()
        phone = "<MISSING>"
        latitude = j.get("latitude") or "<MISSING>"
        longitude = j.get("longitude") or "<MISSING>"
        location_type = "<MISSING>"
        hours = {
            "Monday": {"start": [], "end": []},
            "Tuesday": {"start": [], "end": []},
            "Wednesday": {"start": [], "end": []},
            "Thursday": {"start": [], "end": []},
            "Friday": {"start": [], "end": []},
            "Saturday": {"start": [], "end": []},
            "Sunday": {"start": [], "end": []},
        }

        meals = j.get("meals")
        for m in meals:
            days = m.get("days")
            for d in days:
                hours[d]["start"].append(m.get("start_time"))
                hours[d]["end"].append(m.get("end_time"))

        _tmp = []
        for k, v in hours.items():
            try:
                start = sorted(v["start"])[0]
                end = sorted(v["end"], reverse=True)[0]
                _tmp.append(f"{k}: {start} - {end}")
            except IndexError:
                _tmp.append(f"{k}: Closed")

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
