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
    locator_domain = "https://www.indiabazaar.us/"
    api_url = "https://www.indiabazaar.us/wp-admin/admin-ajax.php?action=store_search&autoload=1"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0"
    }

    session = SgRequests()
    r = session.get(api_url, headers=headers)
    js = r.json()

    for j in js:
        page_url = "https://www.indiabazaar.us/store-locator/"
        location_name = (
            j.get("store")
            .replace("&#8217;", "'")
            .replace("&#038;", "&")
            .replace("&#8211;", "")
            .strip()
        )
        if "(" in location_name:
            hours_of_operation = location_name.split(")")[-1].strip()
            location_name = location_name.split("(")[0].strip()
        else:
            hours_of_operation = location_name.split(":")[-1].strip()
            location_name = location_name.split(":")[0].strip()

        street_address = j.get("address") or "<MISSING>"

        city = j.get("city") or "<MISSING>"
        state = j.get("state") or "<MISSING>"
        postal = j.get("zip") or "<MISSING>"
        country_code = "US"
        store_number = j.get("id") or "<MISSING>"
        phone = j.get("phone") or "<MISSING>"
        latitude = j.get("lat") or "<MISSING>"
        longitude = j.get("lng") or "<MISSING>"
        location_type = "<MISSING>"

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
