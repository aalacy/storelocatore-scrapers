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
    locator_domain = "https://pigtailsandcrewcuts.com"
    api_url = (
        "https://api.zenlocator.com/v1/apps/app_svmnvr56/locations/search?&count=100"
    )

    session = SgRequests()
    r = session.get(api_url)
    js = r.json()["locations"]

    for j in js:
        street_address = (
            f"{j.get('address1')} {j.get('address2') or ''}".strip() or "<INACCESSIBLE>"
        )
        city = j.get("city") or "<INACCESSIBLE>"
        state = j.get("region") or "<INACCESSIBLE>"
        postal = j.get("postcode") or "<INACCESSIBLE>"
        country_code = j.get("countryCode") or "<MISSING>"
        store_number = "<MISSING>"
        location_name = j.get("name")
        latitude = j.get("lat") or "<INACCESSIBLE>"
        longitude = j.get("lng") or "<INACCESSIBLE>"
        location_type = "<MISSING>"
        page_url = "<INACCESSIBLE>"
        phone = "<INACCESSIBLE>"
        contacts = j.get("contacts") or {}
        for v in contacts.values():
            text = v.get("text").strip()
            if text[0].isdigit() or text[0] == "(":
                phone = text
            if text.find("http") != -1:
                page_url = text

        _tmp = []
        hours = j.get("hours").get("hoursOfOperation") or {}
        for k, v in hours.items():
            _tmp.append(f"{k.capitalize()}: {v}")

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
