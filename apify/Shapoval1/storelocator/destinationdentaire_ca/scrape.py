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

    locator_domain = "https://www.destinationdentaire.ca"
    api_url = "https://www.destinationdentaire.ca/wp-admin/admin-ajax.php?action=asl_load_stores&nonce=971a8239f8&load_all=1&layout=1"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()
    for j in js:

        page_url = locator_domain + j.get("website")
        location_name = j.get("title")
        location_type = "<MISSING>"
        street_address = j.get("street")
        state = j.get("state")
        postal = j.get("postal_code")
        country_code = j.get("country")
        city = j.get("city")
        store_number = "<MISSING>"
        latitude = j.get("lat")
        longitude = j.get("lng")
        phone = j.get("phone")
        hours = j.get("open_hours")
        hours = eval(hours)
        days = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
        _tmp = []
        for d in days:
            day = d.capitalize()
            time = hours.get(f"{d}")[0]
            if time == "0":
                time = "Closed"
            line = f"{day} {time}"
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
