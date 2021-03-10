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


def fetch_data():
    out = []
    locator_domain = "https://www.camdennational.com/"
    api_url = "https://www.camdennational.com/_/api/branches/44.209537/-69.064723/500"

    session = SgRequests()
    r = session.get(api_url)
    js = r.json()["branches"]

    for j in js:
        street_address = j.get("address") or "<MISSING>"
        city = j.get("city") or "<MISSING>"
        state = j.get("state") or "<MISSING>"
        postal = j.get("zip") or "<MISSING>"
        country_code = "US"
        store_number = "<MISSING>"
        page_url = "<MISSING>"
        location_name = j.get("name")
        phone = j.get("phone") or "<MISSING>"
        latitude = j.get("lat") or "<MISSING>"
        longitude = j.get("long") or "<MISSING>"
        location_type = "<MISSING>"

        _tmp = []
        text = j.get("description") or "<html></html>"
        tree = html.fromstring(text)
        divs = tree.xpath("//text()")
        divs = list(filter(None, [d.strip() for d in divs]))
        for d in divs:
            if d.find("Drive") != -1 or d.find("Instant") != -1:
                break
            if d.find("Lobby") != -1 or d.find("(") != -1 or d.find("By") != -1:
                continue
            _tmp.append(d)

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
