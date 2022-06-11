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

    locator_domain = "https://tindrumasiankitchen.com/"
    api_url = "https://api.momentfeed.com/v1/analytics/api/llp.json?auth_token=VEQDIXLVCDVXEJHZ&center=33.749,-84.388&coordinates=33.02661951430866,-83.12182568359448,34.46534604926528,-85.65417431640671&multi_account=false&page=1&pageSize=30"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()

    for j in js:
        a = j.get("store_info")
        page_url = a.get("website")
        location_name = a.get("name")
        location_type = "<MISSING>"
        street_address = f"{a.get('address')} {a.get('address_extended')} {a.get('address_3')}".strip()
        phone = a.get("phone")
        state = a.get("region")
        postal = a.get("postcode")
        country_code = a.get("country")
        city = a.get("locality")
        store_number = a.get("corporate_id")
        latitude = a.get("latitude")
        longitude = a.get("longitude")
        hours_of_operation = (
            "".join(a.get("hours"))
            .replace("1,", "Monday ")
            .replace("2,", "Tuesday ")
            .replace("3,", "Wednesday ")
            .replace("4,", "Thursday ")
            .replace("5,", "Friday ")
            .replace("6,", "Saturday ")
            .replace("7,", "Sunday ")
            .replace("00", ".00")
            .replace("30", ".30")
            .replace(",", "-")
            or "<MISSING>"
        )
        cms = "".join(j.get("status"))
        if cms == "coming soon":
            hours_of_operation = "Coming Soon"

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
