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
    locator_domain = "https://www.nicolas.com"
    api_url = "https://www.nicolas.com//en/store-finder?q=London&CSRFToken=11159268-fc5a-48b8-bcbb-82518119c5c1"
    session = SgRequests()
    r = session.get(api_url)
    div = (
        r.text.split("data-stores= '")[1]
        .split("'")[0]
        .strip()
        .replace("\n", "")
        .replace("	", "")
    )
    js = json.loads(div)
    for j in js.values():
        location_name = "".join(j.get("displayName")).replace("&#039;", "`")
        hours_of_operation = "<MISSING>"
        street_address = "".join(j.get("address")).replace("&#039;", "`")
        city = "".join(j.get("town"))
        postal = j.get("postcode")
        state = "<MISSING>"
        page_url = "".join(j.get("urlDetail"))
        page_url = f"{locator_domain}{page_url}"
        country_code = j.get("country")
        if country_code.find("France") != -1:
            continue
        store_number = "<MISSING>"
        latitude = j.get("latitude")
        longitude = j.get("longitude")
        location_type = "<MISSING>"
        phone = "<MISSING>"
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
