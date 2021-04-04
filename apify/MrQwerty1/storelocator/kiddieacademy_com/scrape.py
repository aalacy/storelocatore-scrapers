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


def normalize_hours(hours):
    s = (
        hours.lower()
        .replace("a", "")
        .replace("m", "")
        .replace("p", "")
        .replace(".", "")
        .replace(":", "")
    )
    s = "".join(s.split()).strip()
    start = s.split("-")[0]
    if start[0] == "0":
        start = start[1:]

    end = s.split("-")[1]
    if end[0] == "0":
        end = end[1:]

    start = f"{start[0]}:{start[1:]} am"
    end = f"{end[0]}:{end[1:]} pm"

    return f"{start} - {end}"


def fetch_data():
    out = []
    url = "https://kiddieacademy.com/"
    api_url = "https://kiddieacademy.com/academies/academiesFeed.json"

    session = SgRequests()
    r = session.get(api_url)
    js = r.json()["features"]

    for j in js:
        geo = (
            j.get("geometry").get("coordinates")
            if j.get("geometry")
            else ["<MISSING>", "<MISSING>"]
        )
        j = j["properties"]
        if j.get("status") != "Open":
            continue
        locator_domain = url
        street_address = (
            f"{j.get('address1')} {j.get('address2') or ''}".strip() or "<MISSING>"
        )
        city = j.get("city") or "<MISSING>"
        state = j.get("state") or "<MISSING>"
        postal = j.get("postalCode") or "<MISSING>"
        country_code = j.get("country") or "US"
        if country_code == "USA":
            country_code = "US"

        store_number = j.get("academyNumber") or "<MISSING>"
        page_url = j.get("url") or "<MISSING>"
        location_name = f"Childcare in {city}, {state}"
        phone = j.get("phone") or "<MISSING>"
        latitude = geo[1]
        longitude = geo[0]
        location_type = "<MISSING>"
        hours = j.get("hoursOfOperation") or ""
        if hours:
            if hours.find("M-") != -1:
                days = ""
            else:
                hours = normalize_hours(hours)
                days = "Monday - Friday:"

            hours_of_operation = f"{days} {hours}".strip()
        else:
            hours_of_operation = "<MISSING>"

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
