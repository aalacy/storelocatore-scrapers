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
    locator_domain = "https://barrospizza.com/"
    api_url = "https://cms.barrospizza.com/wp-json/wp/v2/locations?per_page=100&fields=id,slug,acf,title"

    session = SgRequests()
    r = session.get(api_url)
    js = r.json()

    for j in js:
        page_url = f'https://barrospizza.com/locations/{j.get("slug")}/'
        store_number = j.get("id") or "<MISSING>"
        location_name = j.get("title").get("rendered").replace("&#038;", "&")
        j = j.get("acf")

        a = j.get("address")
        street_address = (
            f"{a.get('address_1')} {a.get('address_2') or ''}".strip() or "<MISSING>"
        )
        city = a.get("city") or "<MISSING>"
        state = a.get("state") or "<MISSING>"
        postal = a.get("zip") or "<MISSING>"
        country_code = "US"
        phone = j.get("phone") or "<MISSING>"
        latitude = j.get("latitude") or "<MISSING>"
        longitude = j.get("longitude") or "<MISSING>"
        location_type = "<MISSING>"

        _tmp = []
        sun_thu = j.get("hours_sunday_thursday")
        if sun_thu:
            _tmp.append(f"Sun - Thurs: {sun_thu}")
        fri_sat = j.get("hours_friday_saturday")
        if fri_sat:
            _tmp.append(f"Fri - Sat: {fri_sat}")
        lunch = j.get("hours_lunch")
        if lunch:
            _tmp.append(f"Lunch: {lunch}")

        hours_of_operation = ";".join(_tmp) or "<MISSING>"

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
