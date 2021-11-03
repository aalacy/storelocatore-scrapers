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
    s = set()
    locator_domain = "https://www.usfoods.com/"
    api_url = "https://www.usfoods.com/bin/usfoods/location-query?nocache=true&data={%22locationFallback%22%3A%22locationNoFilters%22%2C%22locationTypes%22%3A[]%2C%22shoppingTypes%22%3A[]%2C%22latitude%22%3A42.4072107%2C%22longitude%22%3A-71.3824374%2C%22distance%22%3A%225000%22}"

    session = SgRequests()
    r = session.get(api_url)
    js = r.json()["message"]

    for j in js:
        street_address = j.get("street") or "<MISSING>"
        city = j.get("city") or "<MISSING>"
        state = j.get("state") or "<MISSING>"
        postal = j.get("postalCode") or "<MISSING>"
        country_code = "US"
        store_number = "<MISSING>"
        page_url = j.get("pagePath")
        location_type = j.get("typeLabel") or "<MISSING>"
        location_name = f"US Foods {location_type}"
        phone = j.get("phone") or "<MISSING>"
        latitude = j.get("latitude") or "<MISSING>"
        longitude = j.get("longitude") or "<MISSING>"
        hours = j.get("generalInfo") or "<MISSING>"
        hours = (
            hours.strip()
            .replace("<p>", "")
            .replace("</p>", "")
            .replace("\n", ";")
            .replace("<br>", "")
            .strip()
        )
        hours_of_operation = hours

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

        check = tuple(row[2:6])
        if check not in s:
            s.add(check)
            out.append(row)

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
