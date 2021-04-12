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

    locator_domain = "https://soupersalad.com/"
    api_url = "https://api.momentfeed.com/v1/analytics/api/llp.json?auth_token=WZTVOSLQVWGVSKZC&center=32.9618,-96.8292&coordinates=31.380978570622688,-94.35178300781247,34.5148372071191,-99.30661699218744&multi_account=false&page=1&pageSize=30"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)

    js = r.json()
    for j in js:
        a = j.get("store_info")
        page_url = a.get("website")
        location_type = "<MISSING>"
        street_address = f"{a.get('address')} {a.get('address_extended')}".replace(
            "None", ""
        ).strip()
        if "".join(a.get("address")).find(a.get("address_extended")) != -1:
            street_address = a.get("address")
        phone = a.get("phone")
        state = a.get("region")
        city = a.get("locality")
        postal = a.get("postcode")
        country_code = a.get("country")
        location_name = a.get("name")
        store_number = "<MISSING>"
        latitude = a.get("latitude")
        longitude = a.get("longitude")
        hours_of_operation = (
            "".join(a.get("hours"))
            .replace("1,", "Monday: ")
            .replace("2,", "Tuesday: ")
            .replace("3,", "Wednesday: ")
            .replace("4,", "Thursday: ")
            .replace("5,", "Friday: ")
            .replace("6,", "Saturday: ")
            .replace("7,", "Sunday: ")
            .replace("00", ".00")
            .replace("30", ".30")
            .replace(";", " ; ")
            .replace(",", "-")
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
