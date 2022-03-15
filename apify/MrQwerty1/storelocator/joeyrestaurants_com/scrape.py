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


def clean_hours(text):
    _tmp = []
    text = (
        text.replace(", ", "|")
        .replace(": ", "|")
        .replace(" to ", " - ")
        .lower()
        .split("|")
    )
    days = [
        "monday",
        "tuesday",
        "wednesday",
        "thursday",
        "friday",
        "saturday",
        "sunday",
    ]
    for t in text:
        t = (
            t.replace("patio open", "")
            .replace("delivery and takeout available", "")
            .replace("open for delivery and takeout", "")
            .replace("open for delivery and pick-up", "")
            .replace("delivery and pick-up", "")
            .strip()
        )
        if "-" in t and "dine-in" not in t:
            _tmp.append(t)
            continue
        if "temporarily" in t:
            _tmp.append(t)
            continue

        for d in days:
            if d in t:
                _tmp.append(t)
                break

    text = ";".join(_tmp)
    separators = [";delivery", ". delivery", "  delivery", ";monday", "until"]
    for sep in separators:
        if sep in text:
            text = text.split(sep)[0].strip()

    if text.endswith("."):
        text = text[:-1]

    return text.replace(";", " ")


def fetch_data():
    out = []
    locator_domain = "https://joeyrestaurants.com/"
    api_url = "https://joeyrestaurants.com/api/restaurants.json"

    session = SgRequests()
    r = session.get(api_url)
    js = r.json()["data"]

    for j in js:
        j = j.get("restaurants")
        street_address = j.get("address") or "<MISSING>"
        city = j.get("city") or "<MISSING>"
        state = j.get("state") or "<MISSING>"
        postal = j.get("postalCode") or "<MISSING>"
        country_code = j.get("country", {}).get("label")
        if country_code == "Canada":
            country_code = "CA"
        else:
            country_code = "US"
        store_number = j.get("id") or "<MISSING>"
        page_url = f'https://joeyrestaurants.com/location/{j.get("slug")}'
        location_name = j.get("title")
        phone = j.get("phone") or "<MISSING>"
        latitude = j.get("latitude") or "<MISSING>"
        longitude = j.get("longitude") or "<MISSING>"
        location_type = "<MISSING>"
        hours_of_operation = j.get("hours") or "<MISSING>"
        hours_of_operation = hours_of_operation.replace("<br />", " ")
        hours_of_operation = clean_hours(hours_of_operation)

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
