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
    locator_domain = "https://cafezupas.com/"
    page_url = "https://cafezupas.com/locations"
    api_url = "https://dev.cafezupas.com/server.php?url=https://api.devcontrolcenter.zupas.com/api/markets/listing"

    session = SgRequests()
    r = session.get(api_url)
    locations = r.json()["data"]["data"]

    for location in locations:
        js = location["locations"]
        for j in js:
            street_address = j.get("address") or "<MISSING>"
            city = j.get("city").replace(" WI", "") or "<MISSING>"
            state = j.get("state") or "<MISSING>"
            postal = j.get("zip") or "<MISSING>"
            country_code = "US"
            store_number = j.get("id") or "<MISSING>"
            location_name = j.get("name")
            phone = j.get("phone") or "<MISSING>"
            latitude = j.get("lat") or "<MISSING>"
            longitude = j.get("long") or "<MISSING>"
            location_type = "<MISSING>"

            _tmp = []
            if j.get("mon_thurs_timings_open"):
                _tmp.append(
                    f'Mon-Thu: {j.get("mon_thurs_timings_open")} - {j.get("mon_thurs_timings_close")}'
                )
            else:
                _tmp.append(f'Mon-Thu: {j.get("mon_thurs_timings")}')

            if j.get("fri_sat_timings_open"):
                _tmp.append(
                    f'Fri-Sat: {j.get("fri_sat_timings_open")} - {j.get("fri_sat_timings_close")}'
                )
            else:
                _tmp.append(f'Fri-Sat: {j.get("fri_sat_timings")}')

            if j.get("sunday_timings"):
                _tmp.append(f'Sun: {j.get("sunday_timings")}')

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
