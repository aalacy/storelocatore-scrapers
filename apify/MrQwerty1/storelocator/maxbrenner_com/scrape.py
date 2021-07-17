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
    locator_domain = "https://maxbrenner.com/"
    api_url = "https://maxbrenner.com/api/data/"

    session = SgRequests()
    r = session.get(api_url)
    locations = r.json()["results"]["locationCollection"]

    for loc in locations:
        js = loc.get("locations") or []

        for j in js:
            street_address = (
                j.get("address")
                .replace("<br />", "")
                .replace("&amp;", "&")
                .replace("\r", "")
                .replace("\n", " ")
                .strip()
                or "<MISSING>"
            )
            city = j.get("city") or "<MISSING>"
            state = j.get("state") or "<MISSING>"
            postal = j.get("code") or "<MISSING>"
            country_code = j.get("country") or "<MISSING>"
            store_number = "<MISSING>"
            page_url = j["metadata"].get("url") or "<MISSING>"
            location_name = f"{j.get('name')} {j.get('subtitle')}".strip()
            phone = j.get("phone") or "<MISSING>"
            latitude = j.get("latitude") or "<MISSING>"
            longitude = j.get("longitude") or "<MISSING>"
            location_type = "<MISSING>"

            _tmp = []
            text = j.get("hours") or "<html></html>"
            tree = html.fromstring(text)
            hours = tree.xpath("//text()")
            for h in hours:
                if not h.strip() or "Sep" in h or "NOV" in h:
                    continue
                _tmp.append(h.strip())

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
