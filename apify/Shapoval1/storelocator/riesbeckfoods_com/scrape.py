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
    locator_domain = "https://www.riesbeckfoods.com"
    api_url = "https://api.freshop.com/1/stores?app_key=riesbeck&has_address=true&limit=-1&token=78e05aaed9d8ca6f32aab783af3bd527"
    session = SgRequests()
    r = session.get(api_url)
    js = r.json()
    for j in js["items"]:
        location_name = j.get("name")
        street_address = j.get("address_1")
        phone = "".join(j.get("phone_md")).replace("\n", "")
        if phone.find("Pharmacy") != -1:
            phone = phone.split("Pharmacy")[0].strip()
        city = j.get("city")
        state = j.get("state")
        country_code = "US"
        store_number = j.get("store_number")
        latitude = j.get("latitude")
        longitude = j.get("longitude")
        location_type = "<MISSING>"
        hours_of_operation = j.get("hours_md")
        page_url = j.get("url")
        postal = j.get("postal_code")
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
