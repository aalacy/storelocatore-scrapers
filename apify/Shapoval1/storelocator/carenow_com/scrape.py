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

    locator_domain = "https://www.carenow.com"
    api_url = "https://www.carenow.com/webcheckin/api/getAllByOrg/0?appCode=WEBCHECKIN"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()

    for j in js:
        page_url = (
            j.get("website") or "https://www.carenow.com/locations/#/clinic-locator"
        )
        location_name = j.get("name")
        location_type = "CareNow"
        street_address = j.get("address") or "<MISSING>"
        phone = j.get("phone") or "<MISSING>"
        state = j.get("state") or "<MISSING>"
        postal = j.get("zip") or "<MISSING>"
        country_code = "US"
        city = j.get("city") or "<MISSING>"
        store_number = j.get("coId") or "<MISSING>"
        latitude = j.get("latitude") or "<MISSING>"
        longitude = j.get("longitude") or "<MISSING>"
        h = j.get("clinicHours")
        hours_of_operation = (
            f"sunday {h.get('sunday')} monday {h.get('monday')} tuesday {h.get('tuesday')} wednesday {h.get('wednesday')} thursday {h.get('thursday')} friday {h.get('friday')} saturday {h.get('saturday')}"
            or "<MISSING>"
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
