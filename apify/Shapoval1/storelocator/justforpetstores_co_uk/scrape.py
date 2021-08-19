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
    locator_domain = "https://www.justforpetstores.co.uk"
    api_url = "https://www.justforpetstores.co.uk/wp-admin/admin-ajax.php?action=store_search&lat=52.9547832&lng=-1.1581086&max_results=5&search_radius=50&autoload=1"
    session = SgRequests()
    r = session.get(api_url)
    js = r.json()

    for j in js:
        street_address = f"{j.get('address')} {j.get('address2')}".strip()
        city = j.get("city") or "<MISSING>"
        state = j.get("state") or "<MISSING>"
        postal = j.get("zip") or "<MISSING>"
        country_code = j.get("country")
        store_number = "<MISSING>"
        page_url = j.get("permalink") or "<MISSING>"
        location_name = j.get("store") or "<MISSING>"
        phone = j.get("phone") or "<MISSING>"
        latitude = j.get("lat") or "<MISSING>"
        longitude = j.get("lng") or "<MISSING>"
        location_type = "<MISSING>"
        hours = j.get("hours")
        tree = html.fromstring(hours)
        days = tree.xpath("//table")
        tmp = []
        for d in days:
            day = " ".join(d.xpath(".//*/text()"))
            tmp.append(day)
        hours_of_operation = ";".join(tmp) or "<MISSING>"

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
