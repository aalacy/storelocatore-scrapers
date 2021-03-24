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
    locator_domain = "https://www.mycountrymart.com"
    api_url = "https://api.freshop.com/1/stores?app_key=mycountrymart&has_address=true&is_selectable=true&limit=5&token=1c7fc988a85c31a0b29c4219996d703a"
    session = SgRequests()

    r = session.get(api_url)
    js = r.json()

    for j in js["items"]:

        street_address = f"{j.get('address_1')} {j.get('address_2')}".replace(
            "None", ""
        ).strip()
        city = j.get("city")
        postal = j.get("postal_code")
        state = j.get("state")
        country_code = "US"
        store_number = j.get("store_number")
        location_name = j.get("name")
        latitude = j.get("latitude")
        longitude = j.get("longitude")
        location_type = "<MISSING>"
        page_url = j.get("url")
        phone = j.get("phone_md")
        hours_of_operation = (
            "".join(j.get("hours_md")).replace("Open", "").replace("\n", "").strip()
        )
        if hours_of_operation.find("First") != -1:
            hours_of_operation = hours_of_operation.split("First")[0].strip()

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
