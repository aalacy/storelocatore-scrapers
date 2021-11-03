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

    locator_domain = "https://www.expeditors.com"
    api_url = "https://www.expeditors.com/locations?json=true"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()
    for j in js:

        page_url = "https://www.expeditors.com/locations"
        location_name = j.get("commonName") or "<MISSING>"
        location_type = j.get("branchType") or "<MISSING>"
        street_address = (
            "".join(j.get("addressLine"))
            .replace("\r\n", " ")
            .replace("\n", " ")
            .strip()
        )
        state = j.get("addressState") or "<MISSING>"
        postal = (
            "".join(j.get("addressPostalCode")).replace("\r\n", " ").strip()
            or "<MISSING>"
        )
        country_code = j.get("addressCountry") or "<MISSING>"
        city = j.get("addressCity") or "<MISSING>"
        store_number = "<MISSING>"
        latitude = j.get("latitude") or "<MISSING>"
        longitude = j.get("longitude") or "<MISSING>"
        phone = (
            "".join(j.get("phoneNumber"))
            .replace("\r\n", " ")
            .replace("\n", " ")
            .strip()
            or "<MISSING>"
        )
        hours_of_operation = "<MISSING>"

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
