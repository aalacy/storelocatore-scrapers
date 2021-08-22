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
    locator_domain = "https://www.goremutual.ca/"
    page_url = locator_domain
    api_url = "https://www.goremutual.ca/wp-content/plugins/superstorefinder-wp/ssf-wp-xml.php?wpml_lang="

    session = SgRequests()
    r = session.get(api_url)
    js = r.json()["item"]

    for j in js:
        line = j.get("address").split("  ")
        if len(line) == 4:
            line.pop(1)
        street_address = line.pop(0).replace("&#44;", ",").strip()
        city = line.pop(0).replace(",", "").strip()
        sp = line.pop(0).strip()
        state = sp.split()[0]
        postal = sp.replace(state, "").strip()
        country_code = "CA"
        store_number = j.get("storeId") or "<MISSING>"
        location_name = j.get("location")
        phone = j.get("telephone") or "<MISSING>"
        latitude = j.get("latitude") or "<MISSING>"
        longitude = j.get("longitude") or "<MISSING>"
        location_type = "<MISSING>"
        hours_of_operation = j.get("operatingHours") or "<MISSING>"

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
