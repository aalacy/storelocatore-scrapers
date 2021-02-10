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
    locator_domain = "https://www.chiquito.co.uk/"
    api_url = "https://www.chiquito.co.uk/api/content/nearest-me"

    session = SgRequests()
    r = session.get(api_url)
    js = r.json()["restaurants"]["fields"]["list"]

    for j in js:
        j = j["fields"]
        street_address = j.get("street") or "<MISSING>"
        city = j.get("city") or "<MISSING>"
        state = j.get("region") or "<MISSING>"
        postal = j.get("postalCode") or "<MISSING>"
        country_code = j.get("country").upper() or "<MISSING>"
        store_number = "<MISSING>"
        page_url = j.get("url") or "<MISSING>"
        location_name = j.get("name")
        phone = j.get("telephone") or "<MISSING>"
        latitude = j.get("latitude") or "<MISSING>"
        longitude = j.get("longitude") or "<MISSING>"
        location_type = "<MISSING>"

        _tmp = []
        days = [
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday",
        ]
        for d in days:
            time = j.get(f"open{d}")
            _tmp.append(f"{d}: {time}")

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

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
