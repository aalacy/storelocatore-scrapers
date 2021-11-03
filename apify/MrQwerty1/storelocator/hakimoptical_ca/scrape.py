import csv

from concurrent import futures
from lxml import html
from sgrequests import SgRequests
from sgzip.static import static_coordinate_list, SearchableCountries


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


def get_data(coord):
    rows = []
    lat, lon = coord
    locator_domain = "https://hakimoptical.ca/"
    api_url = f"https://hakimoptical.ca/wp-admin/admin-ajax.php?action=store_search&lat={lat}&lng={lon}&max_results=50&search_radius=50"

    session = SgRequests()
    r = session.get(api_url)
    js = r.json()
    for j in js:
        page_url = j.get("url") or "<MISSING>"
        if "hakimoptical.ca" not in page_url:
            page_url = "<MISSING>"
        location_name = (
            j.get("store").replace("&#8211;", "-").replace("&#8217;", "'").strip()
        )
        street_address = (
            f"{j.get('address')} {j.get('address2') or ''}".strip() or "<MISSING>"
        )

        city = j.get("city") or "<MISSING>"
        state = j.get("state") or "<MISSING>"
        postal = j.get("zip") or "<MISSING>"
        if ":" in postal:
            postal = postal.split(":")[-1].strip()
        if postal == "Brantford":
            postal = "<MISSING>"
        country_code = "CA"
        store_number = (
            location_name.split()[-1]
            .replace("#", "")
            .replace("(", "")
            .replace(")", "")
            .strip()
        )
        if len(store_number) > 3 and "(" in location_name:
            store_number = location_name.split("(")[-1].replace(")", "").strip()
        phone = j.get("phone") or "<MISSING>"
        if not (phone.startswith("(") or phone[0].isdigit()):
            phone = "<MISSING>"
        latitude = j.get("lat") or "<MISSING>"
        longitude = j.get("lng") or "<MISSING>"
        location_type = "<MISSING>"

        _tmp = []
        hours = j.get("hours") or "<html></html>"
        tree = html.fromstring(hours)
        tr = tree.xpath("//tr")

        for t in tr:
            day = "".join(t.xpath("./td[1]//text()"))
            time = "".join(t.xpath("./td[2]//text()"))
            _tmp.append(f"{day}: {time}")

        hours_of_operation = ";".join(_tmp) or "<MISSING>"

        if location_name.lower().find("closed") != -1:
            hours_of_operation = "Closed"

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

        rows.append(row)

    return rows


def fetch_data():
    out = []
    s = set()
    coords = static_coordinate_list(radius=50, country_code=SearchableCountries.CANADA)

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_data, coord): coord for coord in coords}
        for future in futures.as_completed(future_to_url):
            rows = future.result()
            for row in rows:
                _id = row[8]
                if _id not in s:
                    s.add(_id)
                    out.append(row)

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
