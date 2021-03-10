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
    locator_domain = "https://limefreshmexicangrill.com"
    api_url = "https://limefreshmexicangrill.com/wp-admin/admin-ajax.php?action=store_search&lat=26.3693717&lng=-80.2025238&max_results=25&search_radius=50&autoload=1"

    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0",
        "Accept": "*/*",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "X-Requested-With": "XMLHttpRequest",
        "Proxy-Authorization": "Basic YWNjZXNzX3Rva2VuOmc3NzExNnBzajZqbGZhaHM5dHJwMDdocm0ydTlxNGVzM3BhaGNrYm9oY2kzOGEzMWtpdQ==",
        "Connection": "keep-alive",
        "Referer": "https://limefreshmexicangrill.com/locations/",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
        "TE": "Trailers",
    }

    r = session.get(api_url, headers=headers)
    js = r.json()

    for j in js:

        street_address = "".join(j.get("address"))
        city = "<MISSING>"
        postal = "".join(j.get("zip")) or "<MISSING>"
        state = "<MISSING>"
        phone = "".join(j.get("phone"))
        country_code = "".join(j.get("country"))
        store_number = "<MISSING>"
        location_name = "".join(j.get("store")).replace(" &#8211;", "–").strip()
        latitude = "".join(j.get("lat"))
        longitude = "".join(j.get("lng"))
        location_type = "<MISSING>"
        page_url = "https://limefreshmexicangrill.com/locations/"
        hours = "".join(j.get("description"))
        hours = html.fromstring(hours)
        hours_of_operation = (
            " ".join(hours.xpath('//p/span[contains(text(), "AM")]/text()')).replace(
                "\n", ""
            )
            or "<MISSING>"
        )
        if location_name.find("Orlando") != -1:
            line = j.get("description")
            line = html.fromstring(line)
            add = line.xpath("//p[1]//text()")
            city = "".join(add[1]).split(",")[0]
            state = "".join(add[1]).split(",")[1].strip().split()[0]
            hours_of_operation = " ".join(line.xpath("//p[2]//text()"))
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
