import cloudscraper
import csv


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
    locator_domain = "https://www.car-mart.com/"
    api_url = "https://www.car-mart.com/wp-admin/admin-ajax.php"

    data = {"action": "nearbylots", "lot": "048", "distance": "5000"}

    scraper = cloudscraper.create_scraper()
    r = scraper.post(api_url, data=data)
    js = r.json()

    for j in js:
        location_name = j.get("Name")
        street_address = j.get("Street") or "<MISSING>"
        city = j.get("City") or "<MISSING>"
        state = j.get("State") or "<MISSING>"
        postal = j.get("Zip") or "<MISSING>"
        country_code = "US"
        store_number = j.get("Id")
        page_url = f'https://www.car-mart.com/locations/{store_number}/{city.replace(" ", "-").lower()}'
        phone = j.get("Phone") or "<MISSING>"
        latitude = j.get("Latitude") or "<MISSING>"
        longitude = j.get("Longitude") or "<MISSING>"
        location_type = "<MISSING>"
        hours = j.get("Hours") or "<MISSING>"
        hours_of_operation = " ".join(
            hours.replace("<span>", " ")
            .replace("</span>", "")
            .replace("PM", "PM;")
            .split()
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

        out.append(row)

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
