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

    locator_domain = "https://carylbakervisage.com/"
    api_url = "https://api.storerocket.io/api/user/Kvo8xbj4gn/locations?radius=50&units=kilometers"

    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()["results"]["locations"]
    for j in js:

        slug = j.get("slug")
        page_url = f"https://carylbakervisage.com/pages/locations?location={slug}"
        location_name = j.get("name")
        location_type = "<MISSING>"
        street_address = (
            f"{j.get('address_line_1')} {j.get('address_line_2') or ''}".strip()
        )
        state = j.get("state")
        postal = j.get("postcode")
        country_code = "CA"
        city = j.get("city")
        store_number = "<MISSING>"
        phone = j.get("phone")
        latitude = j.get("lat")
        longitude = j.get("lng")
        days = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
        tmp = []
        for d in days:
            day = d.capitalize()
            time = j.get("hours").get(f"{d}")
            line = f"{day} {time}"
            tmp.append(line)
        hours_of_operation = "; ".join(tmp) or "<MISSING>"
        try:
            tmpcls = j.get("fields")[0].get("pivot_field_value")
        except:
            tmpcls = "<MISSING>"
        if "Temporarily Closed" in tmpcls:
            hours_of_operation = "Temporarily Closed"

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
