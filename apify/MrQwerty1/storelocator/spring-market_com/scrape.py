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


def generate_headers():
    session = SgRequests()
    init = session.post("https://www.spring-market.com/api/m_user/sessioninit")

    token = init.json()[0]
    session_id = init.cookies.get("SSESSff6ed92e85117919b687e9a16062bf17")

    headers = {"X-CSRF-Token": token}
    cookies = {
        "SSESSff6ed92e85117919b687e9a16062bf17": session_id,
        "XSRF-TOKEN": token,
    }
    return headers, cookies


def fetch_data():
    out = []
    url = "https://www.spring-market.com/"

    session = SgRequests()
    headers, cookies = generate_headers()
    r = session.get(
        "https://www.spring-market.com/api/m_store_location?store_type_ids=1,2,3",
        headers=headers,
        cookies=cookies,
    )
    js = r.json()["stores"]

    for j in js:
        locator_domain = url
        _id = j.get("locationID")
        page_url = f"https://www.spring-market.com/stores/{_id}"
        location_name = f"{j.get('storeName')} #{j.get('store_number')}".strip()
        street_address = j.get("address") or "<MISSING>"
        city = j.get("city") or "<MISSING>"
        state = j.get("state") or "<MISSING>"
        postal = j.get("zip") or "<MISSING>"
        country_code = j.get("country") or "<MISSING>"
        store_number = j.get("store_number") or "<MISSING>"
        phone = j.get("phone") or "<MISSING>"
        latitude = j.get("latitude") or "<MISSING>"
        longitude = j.get("longitude") or "<MISSING>"
        location_type = "<MISSING>"

        _tmp = []
        days = [
            "Sunday",
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
        ]
        hours = j.get("store_hours")
        for d, h in zip(days, hours):
            start = h.get("open")
            close = h.get("close")
            _tmp.append(f"{d} {start} - {close}")

        hours_of_operation = ";".join(_tmp) or "<MISSING>"

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
