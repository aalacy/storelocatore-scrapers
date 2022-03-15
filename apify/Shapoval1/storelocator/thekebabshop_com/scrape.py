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


def fetch_data():
    out = []

    locator_domain = "https://thekebabshop.com"
    api_url = "https://cdn4.editmysite.com/app/store/api/v15/editor/users/125785504/sites/989571714618907634/store-locations?page=1&per_page=100&include=address&lang=en&valid=1"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()

    for j in js["data"]:
        page_url = "https://thekebabshop.com/locations/"
        a = j.get("address").get("data")

        location_name = j.get("display_name")
        location_type = "<MISSING>"
        street_address = f"{a.get('street')} {a.get('street2')}".replace(
            "None", ""
        ).strip()
        phone = a.get("phone")
        state = a.get("region_code")
        postal = a.get("postal_code")
        country_code = a.get("country_code")
        city = a.get("city")
        store_number = a.get("store_address_id")
        latitude = a.get("latitude")
        longitude = a.get("longitude")
        hours = j.get("pickup_hours")

        _tmp = []
        for h in hours:
            days = h
            opens = hours.get(h)[0].get("open")
            closes = hours.get(h)[0].get("close")
            line = f"{days} : {opens} - {closes}"
            _tmp.append(line)

        hours_of_operation = "; ".join(_tmp) or "<MISSING>"

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
