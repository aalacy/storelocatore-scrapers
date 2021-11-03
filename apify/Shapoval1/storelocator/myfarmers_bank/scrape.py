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
    locator_domain = "https://www.myfarmers.bank/"
    session = SgRequests()

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0",
    }

    r = session.get(
        "https://www.myfarmers.bank/_/api/branches/33.26738640000001/-93.239115/500",
        headers=headers,
    )
    js = r.json()
    for j in js["branches"]:

        page_url = "https://www.myfarmers.bank/resources/locations-hours"
        street_address = j.get("address") or "<MISSING>"
        city = j.get("city") or "<MISSING>"
        state = j.get("state") or "<MISSING>"
        postal = j.get("zip") or "<MISSING>"
        location_name = j.get("name") or "<MISSING>"
        country_code = "US"
        store_number = "<MISSING>"
        latitude = j.get("lat")
        longitude = j.get("long")
        location_type = "Branch"

        phone = j.get("phone") or "<MISSING>"
        desc = j.get("description")
        h = html.fromstring(desc)
        hours_of_operation = h.xpath("//*//text()")
        hours_of_operation = list(filter(None, [a.strip() for a in hours_of_operation]))
        hours_of_operation = " ".join(hours_of_operation) or "<MISSING>"
        if hours_of_operation.find("Lobby Hours") != -1:
            hours_of_operation = (
                hours_of_operation.split("Lobby Hours")[1].split("Services")[0].strip()
            )
        if (
            hours_of_operation.find("Hours") != -1
            and hours_of_operation.find("Services") != -1
        ):
            hours_of_operation = (
                hours_of_operation.split("Hours")[1].split("Services")[0].strip()
            )
        if (
            hours_of_operation.find("Live Teller Hours") != -1
            and hours_of_operation.find("24/7 ATM") != -1
        ):
            hours_of_operation = (
                hours_of_operation.split("Live Teller Hours")[1]
                .split("24/7 ATM")[0]
                .strip()
            )
        if hours_of_operation.find("Drive-Thru") != -1:
            hours_of_operation = hours_of_operation.split("Drive-Thru")[0].strip()
        if hours_of_operation.find("Drive-thru") != -1:
            hours_of_operation = hours_of_operation.split("Drive-thru")[0].strip()
        hours_of_operation = hours_of_operation.replace(": Monday", "Monday")

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
