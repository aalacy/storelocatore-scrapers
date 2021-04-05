import csv
import json

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


def get_hours(page_url):
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0"
    }
    if not page_url:
        return "<MISSING>"

    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)

    text = "".join(tree.xpath("//span[@data-hours]/@data-hours"))
    if not text:
        return "<MISSING>"

    js = json.loads(text) or {}

    _tmp = []
    for k, v in js.items():
        if v:
            time = " - ".join(v[0])
        else:
            time = "Closed"

        _tmp.append(f"{k}: {time}")

    return ";".join(_tmp) or "<MISSING>"


def fetch_data():
    out = []
    s = set()
    locator_domain = "https://www.therowhouse.com/"
    api_url = "https://members.therowhouse.com/api/brands/therowhouse/locations?&open_status=external"

    session = SgRequests()
    r = session.get(api_url)
    js = r.json()["locations"]

    for j in js:
        street_address = (
            f"{j.get('address')} {j.get('address2') or ''}".strip() or "<MISSING>"
        )
        city = j.get("city") or "<MISSING>"
        state = j.get("state") or "<MISSING>"
        postal = j.get("zip") or "<MISSING>"
        country_code = "US"
        store_number = j.get("seq") or "<MISSING>"
        page_url = j.get("site_url") or "<MISSING>"
        location_name = j.get("name")
        phone = j.get("phone") or "<MISSING>"
        latitude = j.get("lat") or "<MISSING>"
        longitude = j.get("lng") or "<MISSING>"
        location_type = "<MISSING>"
        if j.get("coming_soon"):
            hours_of_operation = "Coming Soon"
        else:
            if page_url != "<MISSING>":
                hours_of_operation = get_hours(page_url)
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

        check = tuple(row[3:6])
        if check not in s:
            s.add(check)
            out.append(row)

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
