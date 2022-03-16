import csv
from lxml import html
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

    locator_domain = "https://www.bankofcastile.com"
    api_url = "https://www.bankofcastile.com/_/api/branches/42.6340526/-78.0482979/5000"
    session = SgRequests()

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()

    for j in js["branches"]:

        page_url = "https://www.bankofcastile.com/locations"
        location_name = j.get("name")
        location_type = "Branch"
        street_address = j.get("address")
        phone = j.get("phone") or "<MISSING>"
        state = j.get("state")
        postal = j.get("zip")
        city = j.get("city")
        country_code = "US"
        store_number = "<MISSING>"
        latitude = j.get("lat")
        longitude = j.get("long")
        hours = j.get("description")
        hours = html.fromstring(hours)
        hours_of_operation = (
            " ".join(hours.xpath("//*//text()"))
            .replace("\n", "")
            .replace("Lobby Hours:", "Lobby Hours")
            .strip()
        )
        if (
            hours_of_operation.find("Lobby Hours") != -1
            and hours_of_operation.find("24 hour") != -1
        ):
            hours_of_operation = (
                hours_of_operation.split("Lobby Hours")[1].split("24 hour")[0].strip()
            )
        if hours_of_operation.find("24-hour") != -1:
            hours_of_operation = hours_of_operation.split("24-hour")[0].strip()
        if hours_of_operation.startswith("Drive-up"):
            hours_of_operation = hours_of_operation.replace(
                "Drive-up Hours", ""
            ).strip()
        if hours_of_operation.find("Drive-up") != -1:
            hours_of_operation = hours_of_operation.split("Drive-up")[0].strip()
        hours_of_operation = hours_of_operation.replace("Lobby Hours", "").strip()
        if hours_of_operation.find("Limited") != -1:
            hours_of_operation = "<MISSING>"

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
