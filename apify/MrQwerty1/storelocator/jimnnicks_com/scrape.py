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
    locator_domain = "https://www.jimnnicks.com/"
    api_url = (
        "https://www.jimnnicks.com/wp-content/themes/jnn/jnn-locations/locations.php"
    )

    session = SgRequests()
    r = session.get(api_url)
    js = r.json()

    for j in js:
        g = j["geometry"]
        j = j["properties"]
        street_address = j.get("address") or "<MISSING>"
        city = j.get("city") or "<MISSING>"
        state = j.get("state") or "<MISSING>"
        postal = j.get("zip") or "<MISSING>"
        country_code = "US"
        store_number = j.get("ID") or "<MISSING>"
        page_url = "https://www.jimnnicks.com/locations/"
        location_name = j.get("store").replace("&#8217;", "'")
        phone = j.get("telephone") or "<MISSING>"
        location_type = "<MISSING>"
        longitude, latitude = g.get("coordinates") or ["<MISSING>", "<MISSING>"]

        _tmp = []
        hours = j.get("hours")
        for h in hours:
            day = h.get("days")
            time = h.get("times")
            _tmp.append(f"{day}: {time}")

        hours_of_operation = ";".join(_tmp) or "<MISSING>"
        if hours_of_operation.find("Temporarily Closed") != -1:
            hours_of_operation = "Temporarily Closed"

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
