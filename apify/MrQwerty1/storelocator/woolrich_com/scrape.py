import csv

from lxml import html
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


def get_token():
    r = session.get("https://www.woolrich.com/us/en/stores")
    tree = html.fromstring(r.text)

    return "".join(tree.xpath("//input[@name='csrf_token']/@value"))


def fetch_data():
    out = []
    locator_domain = "https://www.woolrich.com/"
    token = get_token()
    api_url = f"https://www.woolrich.com/on/demandware.store/Sites-WR_US-Site/en_US/Stores-All?csrf_token={token}"

    r = session.get(api_url)
    js = r.json()["stores"]

    for j in js:
        street_address = (
            f"{j.get('address')} {j.get('address2') or ''}".strip() or "<MISSING>"
        )
        city = j.get("city") or "<MISSING>"
        state = j.get("state") or "<MISSING>"
        postal = j.get("postalCode") or "<MISSING>"
        country_code = j.get("country") or "<MISSING>"
        store_number = j.get("id") or "<MISSING>"
        slug = j.get("url")
        page_url = f"https://www.woolrich.com{slug}"
        location_name = j.get("name")
        phone = j.get("phone") or "<MISSING>"
        latitude = j.get("latitude") or "<MISSING>"
        longitude = j.get("longitude") or "<MISSING>"
        location_type = j.get("storeType") or "<MISSING>"

        _tmp = []
        h = j.get("hours") or {}
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
            part = d[:3]
            start = h.get(f"{part}Start")
            end = h.get(f"{part}End")
            if not start:
                continue
            _tmp.append(f"{d.capitalize()}: {start} - {end}")

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
    session = SgRequests()
    scrape()
