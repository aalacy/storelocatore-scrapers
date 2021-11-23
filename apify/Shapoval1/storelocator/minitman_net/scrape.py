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

    locator_domain = "https://minitman.net/"
    api_url = "https://www.sprintmart.com/wp-admin/admin-ajax.php"
    session = SgRequests()

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0",
        "Accept": "*/*",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "X-Requested-With": "XMLHttpRequest",
        "Origin": "https://www.sprintmart.com",
        "Connection": "keep-alive",
        "Referer": "https://www.sprintmart.com/sprint-mart-locations/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "Cache-Control": "max-age=0",
        "TE": "trailers",
    }

    data = {
        "action": "csl_ajax_onload",
        "address": "",
        "formdata": "addressInput=",
        "lat": "32.416404706713294",
        "lng": "-90.13541521787324",
        "options[distance_unit]": "miles",
        "options[dropdown_style]": "none",
        "options[ignore_radius]": "0",
        "options[immediately_show_locations]": "1",
        "options[initial_radius]": "500",
        "options[label_directions]": "Directions",
        "options[label_email]": "Email",
        "options[label_fax]": "Fax",
        "options[label_phone]": "",
        "options[label_website]": "Website",
        "options[loading_indicator]": "",
        "options[map_center]": "Ridgeland, MS, USA",
        "options[map_center_lat]": "32.416404706713294",
        "options[map_center_lng]": "-90.13541521787324",
        "options[map_domain]": "maps.google.com",
        "options[map_end_icon]": "https://sprintmart.com/wp-content/uploads/2018/01/LocationMarker-1-e1516806074512.png",
        "options[map_home_icon]": "https://sprintmart.com/wp-content/plugins/store-locator-le/images/icons/bulb_lightblue.png",
        "options[map_region]": "us",
        "options[map_type]": "roadmap",
        "options[no_autozoom]": "0",
        "options[use_sensor]": "false",
        "options[zoom_level]": "5",
        "options[zoom_tweak]": "0",
        "radius": "500",
    }

    r = session.post(api_url, headers=headers, data=data)
    js = r.json()["response"]
    for j in js:

        page_url = "https://www.sprintmart.com/sprint-mart-locations/"
        location_name = j.get("name")
        location_type = "<MISSING>"
        street_address = f"{j.get('address')} {j.get('address2')}".strip()
        state = j.get("state") or "<MISSING>"
        postal = j.get("zip") or "<MISSING>"
        country_code = j.get("country") or "US"
        city = j.get("city") or "<MISSING>"
        store_number = "".join(location_name).split("#")[1].strip()
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
