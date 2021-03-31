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
    locator_domain = "https://www.crownwineandspirits.com/"
    page_url = "https://www.crownwineandspirits.com/store-locations/"
    api_url = "https://easylocator.net/ajax/search_by_lat_lon_bounds_geojson/crownwine/53.014783245859235/-100.01953125000001/-53.95608553098789/-261.21093750000006/85.83159098927689/61.17187500000001/0/0/null/null"

    session = SgRequests()
    r = session.get(api_url)
    js = r.json()["physical"]

    for j in js:
        j = j.get("properties")
        street_address = (
            f"{j.get('street_address')} {j.get('street_address_line2') or ''}".strip()
            or "<MISSING>"
        )
        city = j.get("city") or "<MISSING>"
        state = j.get("state_province") or "<MISSING>"
        postal = j.get("zip_postal_code") or "<MISSING>"
        country_code = "US"
        store_number = j.get("location_number").replace("#", "") or "<MISSING>"
        location_name = j.get("name")
        phone = j.get("phone") or "<MISSING>"
        latitude = j.get("lat") or "<MISSING>"
        longitude = j.get("lon") or "<MISSING>"
        location_type = "<MISSING>"

        text = j.get("additional_info") or ""
        text = (
            text.replace("<p>", "")
            .replace("</p>", "")
            .replace("<br />", "")
            .replace("\n", ";")
            .replace("&nbsp;", "")
        )
        hours_of_operation = text or "<MISSING>"

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
