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

    locator_domain = "https://www.fishersfoods.com/"
    api_url = "https://api.freshop.com/1/stores?app_key=fishers_foods&has_address=true&is_selectable=true&token=0dd94e5c5b05730a150f2ae72756fcc5"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()

    for j in js["items"]:

        page_url = j.get("url")
        location_name = j.get("name")
        location_type = j.get("site_name")
        street_address = j.get("address_1")
        state = j.get("state")
        postal = j.get("postal_code")
        country_code = "USA"
        city = j.get("city")
        store_number = j.get("store_number")
        latitude = j.get("latitude")
        longitude = j.get("longitude")
        phone = "".join(j.get("phone_md"))
        if phone.find("\n") != -1:
            phone = phone.split("\n")[0].replace(")4", ") 4").strip()
        hours_of_operation = "".join(j.get("hours_md")).replace("\n", " ").strip()

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
