import csv
import re

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


def get_ids():
    session = SgRequests()
    regex = r'"id":(\d+)'
    r = session.get("https://locations.pret.com/")
    ids = re.findall(regex, r.text)
    return "%2C".join(ids)


def fetch_data():
    out = []
    locator_domain = "https://pret.com/"
    headers = {"x-api-key": "iOr0sBW7MGBg8BDTPjmBOYdCthN3PdaJ"}
    api_url = f"https://gannett-production.apigee.net/store-locator-next/M78JLF3A0MDjQ1ZsZRvNe8912xnGUF/locations-details?locale=en_US&ids={get_ids()}&clientId=5beb07cbf29c525b0c76bc6c&cname=locations.pret.com"
    session = SgRequests()
    r = session.get(api_url, headers=headers)
    js = r.json()["features"]

    for j in js:
        g = j["geometry"]["coordinates"]
        j = j["properties"]
        page_url = f"https://locations.pret.com/{j.get('slug')}"
        location_name = j.get("name") or "<MISSING>"
        street_address = (
            f"{j.get('addressLine1')} {j.get('addressLine2') or ''}" or "<MISSING>"
        )
        city = j.get("city") or "<MISSING>"
        state = j.get("province") or "<MISSING>"
        postal = j.get("postalCode") or "<MISSING>"
        country_code = j.get("country") or "<MISSING>"
        store_number = j.get("branch") or "<MISSING>"
        phone = j.get("phoneLabel") or "<MISSING>"
        if g:
            latitude = g[1]
            longitude = g[0]
        else:
            latitude = "<MISSING>"
            longitude = "<MISSING>"
        location_type = "<MISSING>"

        hours = j.get("hoursOfOperation") or "<MISSING>"
        if hours == "<MISSING>":
            hours_of_operation = hours
        else:
            _tmp = []
            days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
            for d in days:
                if hours.get(d):
                    start = hours.get(d)[0][0]
                    close = hours.get(d)[0][1]
                    _tmp.append(f"{d}: {start} - {close}")
                else:
                    _tmp.append(f"{d}: Closed")

            hours_of_operation = ";".join(_tmp) or "<MISSING>"

            if hours_of_operation.count("Closed") == 7:
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

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
