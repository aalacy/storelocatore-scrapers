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
    s = set()
    locator_domain = "https://www.barburrito.ca/"
    api_url = "https://www.barburrito.ca/wp-admin/admin-ajax.php?lang=en&action=store_search&autoload=1"

    session = SgRequests()
    r = session.get(api_url)
    js = r.json()

    for j in js:
        street_address = (
            f"{j.get('address')} {j.get('address2') or ''}".strip() or "<MISSING>"
        )

        city = j.get("city") or "<MISSING>"
        state = j.get("state") or "<MISSING>"
        postal = j.get("zip") or "<MISSING>"
        country_code = "CA"
        store_number = j.get("id") or "<MISSING>"
        location_name = j.get("store") or "<MISSING>"
        phone = j.get("phone") or "<MISSING>"
        latitude = j.get("lat") or "<MISSING>"
        longitude = j.get("lng") or "<MISSING>"
        location_type = "<MISSING>"
        page_url = j.get("permalink") or "<MISSING>"

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
        text = j.get("hours").split('"')

        for t in text:
            if "{" in t or "}" in t:
                text.pop(text.index(t))

        for d in days:
            index = text.index(d)
            if index == len(text) - 1:
                _tmp.append(f"{d}: Closed")
            else:
                if ":" in text[index + 1]:
                    _tmp.append(f"{d}: {text[index+1]}")
                else:
                    _tmp.append(f"{d}: Closed")

        hours_of_operation = ";".join(_tmp) or "<MISSING>"
        if store_number in s:
            continue
        s.add(store_number)

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
