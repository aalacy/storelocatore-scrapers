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

    locator_domain = "https://www.organicgarage.com/"
    api_url = "https://www.organicgarage.com/wp-admin/admin-ajax.php"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    data = {
        "action": "csl_ajax_onload",
        "address": "",
        "formdata": "addressInput=",
        "lat": "43.7184039",
        "lng": "-79.5181408",
        "radius": "10000",
    }
    r = session.post(api_url, headers=headers, data=data)
    js = r.json()["response"]

    for j in js:

        page_url = "https://www.organicgarage.com/locations"
        location_name = j.get("name")
        location_type = "Organic Garage"
        street_address = f"{j.get('address')} {j.get('address2')}".strip()
        phone = "".join(j.get("phone")).replace("(OG-4-LESS)", "").strip()
        state = j.get("state")
        postal = j.get("zip")
        country_code = "Canada"
        city = "".join(j.get("city")).strip()
        store_number = j.get("id")
        latitude = j.get("lat")
        longitude = j.get("lng")
        hours_of_operation = "".join(j.get("hours")).replace("\r\n", " ").strip()
        if hours_of_operation.find("Coming") != -1:
            continue
        if hours_of_operation.find("We") != -1:
            hours_of_operation = hours_of_operation.split("We")[0].strip()

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
