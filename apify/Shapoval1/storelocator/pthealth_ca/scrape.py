import csv
from lxml import html
from concurrent import futures
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
    lat, lng = coord
    locator_domain = "https://www.pthealth.ca/"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0",
    }

    data = {
        "fac_search_address": "\u041E\u043D\u0442\u0430\u0440\u0438\u043E, \u041A\u0430\u043D\u0430\u0434\u0430",
        "action": "pthealth_find_clinics",
        "lat": f"{lat}",
        "lng": f"{lng}",
    }

    session = SgRequests()

    r = session.post(
        "https://www.pthealth.ca/wp/wp-admin/admin-ajax.php",
        headers=headers,
        data=data,
    )
    js = r.json()
    for j in js.values():

        page_url = j.get("link") or "<MISSING>"
        location_name = j.get("name") or "<MISSING>"
        street_address = (
            "".join(j.get("street_address")).replace("\n", " ").strip() or "<MISSING>"
        )
        city = j.get("city") or "<MISSING>"
        state = j.get("province") or "<MISSING>"
        postal = j.get("postal_code") or "<MISSING>"
        country_code = "CA"
        store_number = "<MISSING>"
        phone = j.get("phone_number") or "<MISSING>"
        latitude = j.get("lat") or "<MISSING>"
        longitude = j.get("lng") or "<MISSING>"
        location_type = "<MISSING>"
        session = SgRequests()
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)
        hours_of_operation = (
            " ".join(tree.xpath('//table[@id="operation-hours"]//tr/td/text()'))
            .replace("\n", "")
            .strip()
            or "<MISSING>"
        )

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
    coords = static_coordinate_list(radius=25, country_code=SearchableCountries.CANADA)

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_data, coord): coord for coord in coords}
        for future in futures.as_completed(future_to_url):
            rows = future.result()
            for row in rows:
                _id = row[3]
                if _id not in s:
                    s.add(_id)
                    out.append(row)

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
