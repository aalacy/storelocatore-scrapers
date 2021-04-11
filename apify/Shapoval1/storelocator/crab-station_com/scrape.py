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

    locator_domain = "https://crab-station.com/"
    tmp = ["1", "2", "3", "4", "5", "6", "8", "9", "10", "43"]
    for i in tmp:
        api_url = f"https://crabstation.revelup.com/weborders/get_initial_data/?establishment={i}"

        session = SgRequests()
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
        }

        r = session.get(api_url, headers=headers)
        js = r.json()["data"]["system_settings"]["data"]

        page_url = f"https://crabstation.revelup.com/weborder/?establishment={i}#about"
        location_name = js["about_title"]

        location_type = "<MISSING>"
        street_address = f"{js['address']['line_1']} {js['address']['line_2']}".strip()
        if street_address.find("(") != -1:
            street_address = street_address.split("(")[0].strip()
        phone = js["phone"]
        state = js["address"]["state"]
        postal = js["address"]["postal_code"]
        country_code = js["address"]["country"]
        city = js["address"]["city"]
        store_number = "".join(i)
        latitude = js["address"]["coordinates"].get("lat")
        longitude = js["address"]["coordinates"].get("lng")

        _tmp = []
        tmp = [
            "monday",
            "tuesday",
            "wednesday",
            "thursday",
            "friday",
            "saturday",
            "sunday",
        ]
        try:
            hours = js["timetables"][0]["timetable_data"]
            for i in tmp:
                days = i
                open = hours.get(i)[0].get("from")
                close = hours.get(i)[0].get("to")
                line = f"{days} - {open} {close}"
                _tmp.append(line)
        except IndexError:
            hours = "<MISSING>"

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
