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
    url = "https://visionworks.com/"

    session = SgRequests()

    for i in range(1, 10000):
        api_url = f"https://api.momentfeed.com/v1/analytics/api/llp.json?auth_token=URTGGJIFYMDMAMXQ&multi_account=true&page={i}&pageSize=100"
        r = session.get(api_url)
        js = r.json()

        for j in js:
            page_url = "https://locations.visionworks.com" + j.get("llp_url")
            j = j["store_info"]
            locator_domain = url
            street_address = (
                f"{j.get('address')} {j.get('address_extended') or ''}".strip()
                or "<MISSING>"
            )
            location_name = j.get("name") or "<MISSING>"
            city = j.get("locality") or "<MISSING>"
            state = j.get("region") or "<MISSING>"
            postal = j.get("postcode") or "<MISSING>"
            if len(postal) == 4:
                postal = f"0{postal}"
            country_code = j.get("country") or "<MISSING>"
            store_number = j.get("corporate_id") or "<MISSING>"
            phone = j.get("phone") or "<MISSING>"
            latitude = j.get("latitude") or "<MISSING>"
            longitude = j.get("longitude") or "<MISSING>"
            location_type = j.get("Type", "<MISSING>")
            hours = j.get("hours")

            if hours:
                _tmp = []
                days = [
                    "Monday",
                    "Tuesday",
                    "Wednesday",
                    "Thursday",
                    "Friday",
                    "Saturday",
                    "Sunday",
                ]
                i = 0
                for d in days:
                    try:
                        line = hours.split(";")[i]
                    except IndexError:
                        line = ""
                    if line.find(",") != -1:
                        start_time = (
                            f'{line.split(",")[1][:2]}:{line.split(",")[1][2:]}'
                        )
                        end_time = f'{line.split(",")[2][:2]}:{line.split(",")[2][2:]}'
                        _tmp.append(f"{d}: {start_time} - {end_time}")
                    else:
                        _tmp.append(f"{d}: Closed")
                    i += 1

                hours_of_operation = ";".join(_tmp) or "<MISSING>"
            else:
                hours_of_operation = "Closed"

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
