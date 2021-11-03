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
    locator_domain = "https://www.lidl.com/"
    api_url = "https://mobileapi.lidl.com/v1/stores?"

    session = SgRequests()
    r = session.get(api_url)
    js = r.json()["results"]

    for j in js:
        a = j.get("address")
        street_address = a.get("street") or "<MISSING>"
        city = a.get("city") or "<MISSING>"
        state = a.get("state") or "<MISSING>"
        postal = a.get("zip") or "<MISSING>"
        country_code = a.get("country") or "<MISSING>"
        store_number = j.get("storeNumber") or "<MISSING>"
        _id = j.get("id")
        page_url = f"https://www.lidl.com/stores/{_id}"
        location_name = j.get("name")
        phone = j.get("phone") or "<MISSING>"
        loc = j.get("coordinates")
        latitude = loc.get("lat") or "<MISSING>"
        longitude = loc.get("lon") or "<MISSING>"
        location_type = "<MISSING>"

        _tmp = []
        hours = j.get("hours", {}).get("regularHours") or []
        for h in hours:
            day = h.get("days")
            time = h.get("hours")
            _tmp.append(f"{day}: {time}")

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
