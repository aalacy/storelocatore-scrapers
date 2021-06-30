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

    locator_domain = "https://pizzashack.ca/"
    api_url = "https://pizzashack.ca/wp-admin/admin-ajax.php?lang=en&action=store_search&lat=47.61835&lng=-65.65134&max_results=25&search_radius=50&autoload=1"

    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()

    for j in js:

        street_address = f"{j.get('address')} {j.get('address2')}".strip()
        city = "".join(j.get("city")) or "<MISSING>"
        postal = j.get("zip") or "<MISSING>"
        state = j.get("state") or "<MISSING>"
        phone = j.get("phone") or "<MISSING>"
        country_code = j.get("country") or "<MISSING>"
        store_number = "<MISSING>"
        location_name = (
            "".join(j.get("store")).replace("&#8211;", "–").replace("&#8217;", "’")
            or "<MISSING>"
        )
        if city.find("Bathurst NB") != -1:
            state = city.split()[1]
            city = city.split()[0]

        latitude = j.get("lat") or "<MISSING>"
        longitude = j.get("lng") or "<MISSING>"
        location_type = "<MISSING>"
        hours_of_operation = "<MISSING>"
        page_url = "https://pizzashack.ca/#locations"
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
