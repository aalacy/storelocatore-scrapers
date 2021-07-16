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

    locator_domain = "https://www.whiskeycake.com/"
    api_url = "https://www.whiskeycake.com/wp-json/wp/v2/location/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()
    for j in js:
        a = j.get("acf")
        page_url = j.get("link")
        location_name = j.get("title").get("rendered")
        location_type = j.get("type")
        street_address = (
            "".join(a.get("address")).replace("<br />", "").replace("  ", " ").strip()
        )
        state = a.get("state")
        postal = a.get("zip")
        city = a.get("city")
        store_number = "<MISSING>"
        country_code = "US"
        latitude = a.get("latitude")
        longitude = a.get("longitude")
        phone = a.get("phone_number")
        hours = a.get("hours")
        tmp = []
        for h in hours:
            day = h.get("day")
            time = h.get("hours")
            line = f"{day} {time}"
            tmp.append(line)
        hours_of_operation = "; ".join(tmp) or "<MISSING>"

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
