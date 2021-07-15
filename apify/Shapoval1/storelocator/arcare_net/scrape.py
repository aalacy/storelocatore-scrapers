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

    locator_domain = "https://www.arcare.net"
    api_url = "https://www.arcare.net/wp-admin/admin-ajax.php"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
        "Accept": "*/*",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "X-Requested-With": "XMLHttpRequest",
        "Origin": "https://www.arcare.net",
        "Connection": "keep-alive",
        "Referer": "https://www.arcare.net/locations/",
        "TE": "Trailers",
    }

    data = {
        "action": "csl_ajax_search",
        "address": "",
        "formdata": "addressInput=",
        "lat": "35.29341423323972",
        "lng": "-91.4655415",
        "options[distance_unit]": "miles",
        "options[dropdown_style]": "none",
        "options[ignore_radius]": "0",
        "options[immediately_show_locations]": "0",
        "options[initial_radius]": "500",
        "options[label_directions]": "Get Directions",
        "options[label_email]": "Email",
        "options[label_fax]": "Fax",
        "options[label_phone]": "Phone",
        "options[label_website]": "Clinic Information",
        "options[loading_indicator]": "",
        "options[map_center]": "Augusta AR",
        "options[map_center_lat]": "35.2823079",
        "options[map_center_lng]": "-91.36540629999999",
        "options[map_domain]": "maps.google.com",
        "options[map_end_icon]": "https://www.arcare.net/wp-content/plugins/store-locator-le/images/icons/bulb_azure.png",
        "options[map_home_icon]": "https://www.arcare.net/wp-content/plugins/store-locator-le/images/icons/bulk_blue.png",
        "options[map_region]": "us",
        "options[map_type]": "roadmap",
        "options[no_autozoom]": "0",
        "options[use_sensor]": "false",
        "options[zoom_level]": "8",
        "options[zoom_tweak]": "0",
        "radius": "500",
    }
    r = session.post(api_url, headers=headers, data=data)
    js = r.json()["response"]
    for j in js:

        page_url = "https://www.arcare.net/locations/"
        location_name = j.get("name") or "<MISSING>"
        location_type = "<MISSING>"
        street_address = (
            f"{j.get('address')} {j.get('address2')}".strip() or "<MISSING>"
        )
        state = j.get("state") or "<MISSING>"
        postal = j.get("zip") or "<MISSING>"
        country_code = "US"
        city = j.get("city") or "<MISSING>"
        store_number = "<MISSING>"
        latitude = j.get("lat") or "<MISSING>"
        longitude = j.get("lng") or "<MISSING>"
        phone = j.get("phone") or "<MISSING>"
        hours_of_operation = j.get("hours") or "<MISSING>"

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
