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


def get_data(j):
    locator_domain = "https://www.needs.ca/"
    location_name = j.get("name") or "<MISSING>"
    street_address = j.get("address_1") or "<MISSING>"
    city = j.get("city") or "<MISSING>"
    text = j.get("post_content", "") or ""
    if text:
        state = text.split(",")[-1].strip().split()[0].strip()
    else:
        state = "<MISSING>"

    postal = j.get("postal_code_org") or "<MISSING>"
    country_code = "CA"
    store_number = j.get("store_number") or "<MISSING>"
    page_url = "<MISSING>"
    phone = j.get("phone") or "<MISSING>"
    latitude = j.get("lat") or "<MISSING>"
    longitude = j.get("lng") or "<MISSING>"
    location_type = "<MISSING>"

    _tmp = []
    hours = j.get("hours", []) or []
    for h in hours:
        day = h.get("day")
        time = h.get("hours") or "Closed"
        _tmp.append(f"{day}: {time}")

    hours_of_operation = ";".join(_tmp) or "<MISSING>"

    if hours_of_operation.count("Closed") == 7:
        hours_of_operation = "<MISSING>"
    elif hours_of_operation.count("Open 24 Hours") == 7:
        hours_of_operation = "Open 24 Hours"

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

    return row


def fetch_data():
    out = []
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:83.0) Gecko/20100101 Firefox/83.0"
    }

    for i in range(1, 5000):
        data = {
            "action": "search_nearest_stores",
            "lng": "34.5407",
            "lat": "49.5937",
            "page": i,
        }

        r = session.post(
            "https://www.needs.ca/wp-admin/admin-ajax.php", data=data, headers=headers
        )
        js = r.json()["stores"]

        if isinstance(js, dict):
            js = js.values()

        for j in js:
            j = j["store"]
            row = get_data(j)
            out.append(row)

        if len(js) < 6:
            break

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
