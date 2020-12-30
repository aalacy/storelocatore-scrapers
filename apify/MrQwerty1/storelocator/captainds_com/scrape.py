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
    locator_domain = "https://captainds.com/"

    session = SgRequests()

    for i in range(1, 10000):
        api_url = f"https://api.momentfeed.com/v1/analytics/api/llp.json?auth_token=AJXCZOENNNXKHAKZ&pageSize=100&page={i}"
        r = session.get(api_url)
        js = r.json()

        for j in js:
            j = j["store_info"]
            page_url = j.get("website") or "<MISSING>"
            street_address = j.get("address") or "<MISSING>"
            location_name = f"{j.get('name')} {street_address}".encode(
                "ascii", "ignore"
            ).decode()
            if (
                location_name.lower().find("closed") != -1
                or location_name.lower().find("coming") != -1
            ):
                continue
            city = j.get("locality") or "<MISSING>"
            state = j.get("region") or "<MISSING>"
            postal = j.get("postcode") or "<MISSING>"
            country_code = j.get("country") or "<MISSING>"
            store_number = "<MISSING>"
            phone = j.get("phone") or "<MISSING>"
            latitude = j.get("latitude") or "<MISSING>"
            longitude = j.get("longitude") or "<MISSING>"
            location_type = j.get("Type", "<MISSING>")
            hours = j.get("hours") or "<MISSING>"

            if hours == "<MISSING>":
                hours_of_operation = hours
            else:
                _tmp = []
                days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
                for d, line in zip(days, hours.split(";")):
                    start_time = f'{line.split(",")[1][:2]}:{line.split(",")[1][2:]}'
                    end_time = f'{line.split(",")[2][:2]}:{line.split(",")[2][2:]}'
                    _tmp.append(f"{d}: {start_time} - {end_time}")
                hours_of_operation = ";".join(_tmp)

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
        if len(js) < 100:
            break

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
