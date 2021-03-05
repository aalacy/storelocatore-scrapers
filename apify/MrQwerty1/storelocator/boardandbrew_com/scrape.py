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
    locator_domain = "https://boardandbrew.com/"
    api_url = "https://boardandbrew.com/wp-admin/admin-ajax.php?action=store_search&autoload=1"

    session = SgRequests()
    r = session.get(api_url)
    js = r.json()

    for j in js:
        street_address = f"{j.get('address')} {j.get('address2') or ''}".strip()
        city = j.get("city") or "<MISSING>"
        state = j.get("state") or "<MISSING>"
        postal = j.get("zip") or "<MISSING>"
        country_code = "US"
        store_number = j.get("id") or "<MISSING>"
        page_url = j.get("url") or "<MISSING>"
        location_name = j.get("store")
        phone = j.get("phone") or "<MISSING>"
        if "walk" in phone.lower():
            phone = "<MISSING>"
        latitude = j.get("lat") or "<MISSING>"
        longitude = j.get("lng") or "<MISSING>"
        location_type = "<MISSING>"

        _tmp = []
        text = j.get("hours") or "<html></html>"
        tree = html.fromstring(text)
        tr = tree.xpath("//tr")
        for t in tr:
            day = "".join(t.xpath("./td[1]//text()")).strip()
            time = "".join(t.xpath("./td[2]//text()")).strip()
            _tmp.append(f"{day}: {time}")

        hours_of_operation = ";".join(_tmp) or "<MISSING>"
        if "<" in location_name:
            location_name = location_name.split("<")[0].strip()
            hours_of_operation = "Coming Soon"

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
