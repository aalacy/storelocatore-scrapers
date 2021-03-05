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
    locator_domain = "https://bareburger.com/"
    headers = {"Client": "bareburger"}

    session = SgRequests()
    r = session.post("https://patron.lunchbox.io/v0/locations", headers=headers)
    js = r.json()

    for j in js:
        a = j.get("address")
        street_address = (
            f"{a.get('street1')} {a.get('street2') or ''}".strip() or "<MISSING>"
        )
        city = a.get("city") or "<MISSING>"
        state = a.get("state") or "<MISSING>"
        postal = a.get("zip") or "<MISSING>"
        if len(postal) == 6:
            postal = postal[1:]
        country_code = "US"
        store_number = "<MISSING>"
        location_name = j.get("name")
        slug = j.get("slug") or location_name
        page_url = f"https://order.bareburger.com/location/{slug}"
        phone = j.get("phone").get("value") or "<MISSING>"
        loc = a.get("geo")
        latitude = loc.get("lat") or "<MISSING>"
        longitude = loc.get("long") or "<MISSING>"
        location_type = "<MISSING>"

        _tmp = []
        days = [
            "Sunday",
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
        ]
        hours = j.get("hours") or []
        for h in hours:
            index = h.get("day")
            day = days[index]
            start = h.get("dineInOpen")
            close = h.get("dineInClose")
            _tmp.append(f"{day}: {start} - {close}")

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
