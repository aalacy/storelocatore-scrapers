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
    locator_domain = "https://thebankofprinceton.com/"
    api_url = (
        "https://thebankofprinceton.com/_/api/branches/40.3558542/-74.6695045/5000"
    )

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
        page_url = "https://thebankofprinceton.com/contact/locations-and-hours"
        location_name = j.get("name")
        phone = j.get("phone") or "<MISSING>"
        latitude = j.get("lat") or "<MISSING>"
        longitude = j.get("long") or "<MISSING>"
        location_type = "<MISSING>"

        _tmp = []
        text = j.get("description") or "<html></html>"
        tree = html.fromstring(text)
        divs = tree.xpath("//text()")
        for d in divs:
            if "Temporarily Closed" in d:
                _tmp.append("Temporarily Closed")
                break
            if "Drive" in d:
                break
            if not d.strip() or "Hours" in d or "Safe" in d:
                continue
            _tmp.append(d.replace("\xa0", " ").replace("\n", "").strip())

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
