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

    locator_domain = "https://banksouthern.com"
    api_url = "https://banksouthern.com/?hcs=locatoraid&hca=search%3Asearch%2F%2Fproduct%2F3%2Flat%2F%2Flng%2F%2Flimit%2F100%2Fproduct2%2F3"
    session = SgRequests()

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    js = r.json()["results"]
    for j in js:
        page_url = "https://banksouthern.com/locations/"
        location_name = j.get("name")
        location_type = "ATM"
        street_address = f"{j.get('street1')} {j.get('street2')}".strip()
        phone = j.get("phone") or "<MISSING>"
        if phone != "<MISSING>":
            phone = html.fromstring(phone)
            phone = "".join(phone.xpath("//a//text()"))
        state = j.get("state")
        postal = j.get("zip")
        city = j.get("city")
        country_code = "US"
        store_number = j.get("id")
        latitude = j.get("latitude")
        longitude = j.get("longitude")
        hours_of_operation = f"{j.get('misc1')} {j.get('misc2')}".strip() or "<MISSING>"
        if hours_of_operation == "<MISSING>" or hours_of_operation == "NO LOBBY HOURS":
            hours_of_operation = (
                f"{j.get('misc3')} {j.get('misc4')}".strip() or "<MISSING>"
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
