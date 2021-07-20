import csv
import html

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
    locator_domain = "https://burberry.com"

    session = SgRequests()
    r = session.get("https://api.burberry.com/services/sites/v1?language=en&limit=1000")
    js = r.json()["data"]

    for j in js:
        slug = j.get("store_page_url")
        a = j.get("address") or {}
        street_address = a.get("line2") or "<MISSING>"
        city = a.get("city") or "<MISSING>"
        location_name = html.unescape(
            f"{city or ''} {j.get('public_name_en') or ''}".strip()
        )
        state = a.get("state") or "<MISSING>"
        postal = a.get("postcode") or "<MISSING>"
        if "AB " in postal:
            postal = postal.replace("AB ", "")
        if postal == "--":
            postal = "<MISSING>"
        country_code = a.get("country") or "<MISSING>"
        store_number = j.get("id") or "<MISSING>"
        country = a.get("country_name")

        if slug:
            page_url = f"https://us.burberry.com{slug}"
        else:
            if country:
                page_url = f"https://us.burberry.com/store-locator/{country.replace(' ', '-').lower()}/"
            else:
                continue
        phone = j.get("phone") or "<MISSING>"
        latitude = j.get("latitude") or "<MISSING>"
        longitude = j.get("longitude") or "<MISSING>"
        location_type = j.get("type") or "<MISSING>"

        _tmp = []
        days = [
            "monday",
            "tuesday",
            "wednesday",
            "thursday",
            "friday",
            "saturday",
            "sunday",
        ]
        for d in days:
            if not j["opening_times"][d]:
                continue
            start = j["opening_times"][d]["hours"][0]["from"]
            close = j["opening_times"][d]["hours"][0]["to"]
            if not start or not close:
                _tmp.append(f"{d[:3].capitalize()}: closed")
            else:
                _tmp.append(f"{d[:3].capitalize()}: {start} - {close}")

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
