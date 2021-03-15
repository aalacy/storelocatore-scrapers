import csv
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
    locator_domain = "https://locations.thebay.com"
    api_url = "https://locations.thebay.com/en-ca/api/v2/stores.json"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0",
        "Accept": "*/*",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "X-Requested-With": "XMLHttpRequest",
        "Connection": "keep-alive",
        "Referer": "https://locations.thebay.com/en-ca?",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()
    for j in js["stores"]:
        street_address = f"{j.get('address_1')} {j.get('address_2')}".replace(
            "None", ""
        ).strip()
        city = j.get("city")
        state = j.get("state")
        postal = j.get("postal_code")
        country_code = j.get("country_code")
        store_number = j.get("number")
        location_name = j.get("name")
        phone = j.get("phone_number")
        page_url = f"{locator_domain}{j.get('url')}"
        latitude = j.get("latitude")
        longitude = j.get("longitude")
        location_type = j.get("type").get("name")
        hours = j.get("regular_hour_ranges")
        tmp = []
        for h in hours:
            days = h.get("days")
            hours = h.get("hours")
            line = f"{days} : {hours}"
            tmp.append(line)
        hours_of_operation = (
            ";".join(tmp).replace("&#8211;", "-").strip() or "<MISSING>"
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


def scrape():
    data = get_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
