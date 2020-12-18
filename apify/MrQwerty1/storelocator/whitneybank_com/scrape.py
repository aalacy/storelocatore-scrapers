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
    locator_domain = "https://www.hancockwhitney.com/"
    api_url = "https://hancockwhitney-api-production.herokuapp.com/location?latitude=33.0218117&locationTypes=branch,business&longitude=-97.1251&pageSize=5000&radius=5000"

    session = SgRequests()
    r = session.get(api_url)
    js = r.json()["data"]

    for j in js:
        location_name = j.get("name") or "<MISSING>"
        a = j.get("address", {}) or {}
        street_address = a.get("street") or "<MISSING>"
        city = a.get("city") or "<MISSING>"
        state = a.get("state") or "<MISSING>"
        postal = a.get("zip") or "<MISSING>"
        country_code = "US"
        store_number = "<MISSING>"
        page_url = "<MISSING>"
        phone = j.get("phone") or "<MISSING>"
        geo = j.get("geo", {}).get("coordinates") or ["<MISSING>", "<MISSING>"]
        latitude = geo[1]
        longitude = geo[0]
        location_type = ",".join(j.get("locationTypes")) or "<MISSING>"

        hours_of_operation = (
            j.get("lobbyHours").replace("(appointment only)", "") or "<MISSING>"
        )
        if hours_of_operation.find("(") != -1:
            hours_of_operation = hours_of_operation.split("(")[0].strip()

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
