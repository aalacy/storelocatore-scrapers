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


def get_data():
    rows = []
    locator_domain = "https://atlantabread.com/"
    api_url = "https://atlantabread.com/wp-admin/admin-ajax.php?action=store_search&lat=33.748995&lng=-84.387982&max_results=500&radius=20&autoload=1"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0",
        "Accept": "*/*",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "X-Requested-With": "XMLHttpRequest",
        "Connection": "keep-alive",
        "Referer": "https://atlantabread.com/locations/",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
        "TE": "Trailers",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()
    for j in js:
        street_address = f"{j.get('address')} {j.get('address2')}".replace(
            "None", ""
        ).strip()
        city = j.get("city")
        state = j.get("state")
        postal = j.get("zip")
        country_code = "US"
        store_number = "<MISSING>"
        location_name = j.get("store")
        phone = j.get("phone")
        page_url = j.get("permalink")
        latitude = j.get("lat")
        longitude = j.get("lng")
        location_type = "<MISSING>"
        hours = j.get("hours")
        block = html.fromstring(hours)

        hours_of_operation = (
            "".join(block.xpath("//*//text()")).replace("\n", "").strip() or "<MISSING>"
        )
        if hours_of_operation.count("Closed on") == 7:
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


def scrape():
    data = get_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
