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
    locator_domain = "https://www.rocklandtrust.com/"
    api_url = "https://www.rocklandtrust.com/_/api/branches/0/0/10000"

    session = SgRequests()
    r = session.get(api_url)
    js = r.json()["branches"]

    for j in js:
        text = j.get("description") or "<html></html>"
        tree = html.fromstring(text)
        street_address = j.get("address") or "<MISSING>"
        city = j.get("city") or "<MISSING>"
        state = j.get("state") or "<MISSING>"
        postal = j.get("zip") or "<MISSING>"
        country_code = "US"
        store_number = "<MISSING>"
        page_url = (
            tree.xpath("//a[not(contains(@href, 'mailto'))]/@href")[0] or "<MISSING>"
        )
        location_name = j.get("name") or "<MISSING>"
        phone = j.get("phone") or "<MISSING>"
        latitude = j.get("lat") or "<MISSING>"
        longitude = j.get("long") or "<MISSING>"
        location_type = "<MISSING>"

        hours = tree.xpath(
            "//*[contains(text(), ': ') or contains(text(), 'Drive') or contains(text(), 'Teller Hours')]/text()"
        )
        hours = list(filter(None, [h.strip() for h in hours]))
        hours = ";".join(hours).replace("\n", "")
        if hours.find("Drive") != -1:
            hours = hours.split("Drive")[0]
        elif hours.find("Teller") != -1:
            hours = hours.split("Teller")[0]

        hours_of_operation = hours or "<MISSING>"

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
