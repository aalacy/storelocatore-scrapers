import csv
import json
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
    locator_domain = "https://stokesmarket.com/"
    api_url = "https://afsshareportal.com/lookUpFeatures.php?action=storeInfo&website_url=stokesmarket.com"

    session = SgRequests()
    r = session.get(api_url)
    js = json.loads(r.text[1:-1])

    for j in js:
        street_address = j.get("store_address") or "<MISSING>"
        city = j.get("store_city") or "<MISSING>"
        state = j.get("store_state") or "<MISSING>"
        postal = j.get("store_zip") or "<MISSING>"
        country_code = "US"
        store_number = j.get("store_id") or "<MISSING>"
        page_url = f"https://stokesmarket.com/{city.lower()}"
        location_name = j.get("store_name")
        phone = j.get("store_phone") or "<MISSING>"
        latitude = j.get("store_lat") or "<MISSING>"
        longitude = j.get("store_lng") or "<MISSING>"
        location_type = "<MISSING>"
        _tmp = [
            f'Mon-Fri: {j.get("store_hMonOpen")} - {j.get("store_hMonClose")}',
            f'Sat: {j.get("store_hSatOpen")} - {j.get("store_hSatClose")}',
            f'Sun: {j.get("store_hSunOpen")} - {j.get("store_hSunClose")}',
        ]
        hours_of_operation = (
            ";".join(_tmp).replace("Closed - Closed", "Closed") or "<MISSING>"
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
