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
    locator_domain = "https://papersource.com"
    session = SgRequests()

    for i in range(5000):
        api_url = f"https://store-locator.papersource.com/api/stores/?page={i}"
        r = session.get(api_url)
        js = r.json()["data"]["rows"]

        for j in js:
            street_address = (
                f"{j.get('address_1')} {j.get('address_2') or ''}".strip()
                or "<MISSING>"
            )
            city = j.get("city") or "<MISSING>"
            state = j.get("state") or "<MISSING>"
            postal = j.get("postal_code") or "<MISSING>"
            if len(postal) == 4:
                postal = f"0{postal}"
            country_code = j.get("country_code") or "<MISSING>"
            if country_code == "United States":
                country_code = "US"

            store_number = j.get("id") or "<MISSING>"
            page_url = (
                f'https://store-locator.papersource.com/locations/store/{j.get("slug")}'
            )
            location_name = j.get("store_name") or "<MISSING>"
            phone = j.get("phone_number") or "<MISSING>"
            latitude = j.get("latitude") or "<MISSING>"
            longitude = j.get("longitude") or "<MISSING>"
            location_type = "<MISSING>"

            _tmp = []
            hours = j.get("store_timings", []) or []
            for h in hours:
                day = h.get("day")
                start = h.get("from_time")
                end = h.get("to_time")
                if start == "Closed":
                    _tmp.append(f"{day}: Closed")
                else:
                    _tmp.append(f"{day}: {start} - {end}")

            hours_of_operation = ";".join(_tmp) or "<MISSING>"

            if hours_of_operation.count("Closed") == 7:
                hours_of_operation = "Closed"

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

        if len(js) < 10:
            break

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
