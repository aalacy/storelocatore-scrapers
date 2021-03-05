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


def clean_phone(text):
    _tmp = []
    for t in text:
        if t.isdigit():
            _tmp.append(t)

    if len(_tmp) == 10:
        _tmp = "".join(_tmp)
        return "({}) {}-{}".format(_tmp[:3], _tmp[3:6], _tmp[6:])
    else:
        return "<MISSING>"


def fetch_data():
    out = []
    locator_domain = "https://www.mrpickles.com/"
    api_url = "https://www.mrpickles.com/wp-json/wp/v2/location?per_page=100"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:84.0) Gecko/20100101 Firefox/84.0"
    }

    session = SgRequests()
    r = session.get(api_url, headers=headers)
    js = r.json()

    for j in js:
        page_url = j.get("link")
        location_name = (
            j.get("title")
            .get("rendered")
            .replace("&#8217;", "'")
            .replace("&#8211;", "–")
        )
        a = j.get("acf")
        street_address = (
            f"{a.get('street')} {a.get('suite') or ''} {a.get('street2') or ''}".strip()
            or "<MISSING>"
        )
        city = a.get("city") or "<MISSING>"
        state = a.get("state") or "<MISSING>"
        postal = a.get("zip") or "<MISSING>"
        country_code = "US"
        store_number = a.get("store_number") or "<MISSING>"
        phone = a.get("phone") or "<MISSING>"
        phone = clean_phone(phone)
        latitude = a.get("google_map").get("lat") or "<MISSING>"
        longitude = a.get("google_map").get("lng") or "<MISSING>"
        location_type = "<MISSING>"

        _tmp = []
        hours = a.get("hours") or []

        for h in hours:
            day = h.get("days")
            time = h.get("hours")
            if day:
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
