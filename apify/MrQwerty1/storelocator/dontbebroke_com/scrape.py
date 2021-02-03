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
    locator_domain = "https://www.dontbebroke.com/"
    api_url = "https://www.dontbebroke.com/api/v1/yext/locations/get/"

    session = SgRequests()
    r = session.get(api_url)
    js = r.json()["locations"]

    for j in js:
        street_address = j.get("address") or "<MISSING>"
        city = j.get("city") or "<MISSING>"
        state = j.get("state") or "<MISSING>"
        postal = j.get("zip") or "<MISSING>"
        country_code = j.get("countryCode") or "<MISSING>"
        store_number = j.get("id") or "<MISSING>"
        page_url = f'https://www.dontbebroke.com/locations/{j.get("slug")}'
        location_name = j.get("locationName")
        phone = j.get("phone") or "<MISSING>"
        latitude = j.get("displayLat") or "<MISSING>"
        longitude = j.get("displayLng") or "<MISSING>"
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
        hours = j.get("hours")

        for h in hours.split(","):
            if not h:
                continue
            index = int(h.split(":")[0]) - 2
            day = days[index]
            time = ":".join(h.split(":")[1:])
            _tmp.append(f"{day}: {time}")

        hours_of_operation = ";".join(_tmp) or "<MISSING>"
        if location_name.find("Permanently Closed") != -1:
            continue
        elif location_name.find("Closed") != -1:
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
