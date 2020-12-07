import csv
import json

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
    locator_domain = "https://www.saq.com"

    session = SgRequests()
    headers = {"X-Requested-With": "XMLHttpRequest"}

    for i in range(0, 10000, 10):
        api_url = f"https://www.saq.com/en/store/locator/ajaxlist/?loaded={i}"
        r = session.get(api_url, headers=headers)
        js = r.json()["list"]

        for j in js:
            location_name = j.get("name") or "<MISSING>"
            street_address = f"{j.get('address1')}".strip() or "<MISSING>"
            city = j.get("city") or "<MISSING>"
            state = j.get("region") or "<MISSING>"
            postal = j.get("postcode") or "<MISSING>"
            country_code = j.get("country_id") or "<MISSING>"
            store_number = j.get("identifier")
            page_url = f"https://www.saq.com/en/store/{store_number}"
            phone = j.get("telephone") or "<MISSING>"
            latitude = j.get("latitude") or "<MISSING>"
            longitude = j.get("longitude") or "<MISSING>"
            location_type = "<MISSING>"

            _tmp = []
            hours = json.loads(j.get("opening_hours", ""))
            for h in hours:
                day = h.get("dayLabel")
                start = h.get("open_formatted")
                close = h.get("close_formatted")

                if not start:
                    _tmp.append(f"{day}: Closed")
                else:
                    _tmp.append(f"{day}: {start} - {close}")

            hours_of_operation = ";".join(_tmp) or "<MISSING>"

            if hours_of_operation.count("Closed") == 7:
                continue

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
        if len(js) < 10:
            break

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
