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
    locator_domain = "https://giardinosalads.com"
    api_url = "https://order.giardinosalads.com/api/vendors/search/FL"

    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0",
        "X-Olo-Request": "1",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()
    for j in js["vendor-search-results"]:
        a = j.get("address")
        street_address = f"{a.get('streetAddress')} {a.get('streetAddress2')}".strip()
        city = a.get("city")
        postal = a.get("postalCode")
        state = a.get("state")
        country_code = a.get("country")
        store_number = "<MISSING>"
        slug = "".join(j.get("slug"))
        page_url = f"https://order.giardinosalads.com/menu/{slug}"
        location_name = j.get("name")
        phone = j.get("phoneNumber")
        latitude = j.get("latitude")
        longitude = j.get("longitude")
        location_type = "<MISSING>"
        hours = j.get("weeklySchedule")["calendars"]
        hourses = hours[0].get("schedule")
        tmp = []
        for h in hourses:
            day = h.get("weekDay")
            time = h.get("description")
            line = f"{day} - {time}"
            tmp.append(line)
        hours_of_operation = ";".join(tmp) or "<MISSING>"
        if hours_of_operation.count("Closed") == 7:
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
        out.append(row)

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
