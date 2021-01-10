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
    url = "https://www.tdameritrade.com/"
    api_url = "https://www.tdameritrade.com/branchlocator/tda-locations/json/branches_data.json"

    session = SgRequests()
    r = session.get(api_url)
    js = r.json()["all"]

    for j in js:
        locator_domain = url
        a = j.get("addr")
        street_address = (
            f"{a.get('street')} {a.get('line_two') or ''}".strip() or "<MISSING>"
        )
        city = a.get("city") or "<MISSING>"
        state = a.get("state") or "<MISSING>"
        postal = a.get("zip") or "<MISSING>"
        country_code = "US"

        store_number = j.get("tda_id") or "<MISSING>"
        page_url = f'https://www.tdameritrade.com{j.get("url")}'
        location_name = j.get("headline")
        if not location_name:
            location_name = j.get("page_title").split(" | ")[1]
        phone = j.get("phone") or "<MISSING>"
        loc = j.get("coords")
        latitude = loc.get("y") or "<MISSING>"
        longitude = loc.get("x") or "<MISSING>"
        location_type = "Branch"
        hours_of_operation = f'M-F: {j.get("hours")}'

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
