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

    locator_domain = "https://www.everythingwine.ca"
    api_url = "https://www.everythingwine.ca/storelocator/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    jsblock = "".join(
        tree.xpath('//script[contains(text(), "place_id")]/text()')
    ).replace("\\", "")
    jsblock = jsblock.split('"}}"},')

    for j in jsblock:

        page_url = "https://www.everythingwine.ca/storelocator/"
        location_name = j.split('"name":"')[1].split('"')[0].strip()
        location_type = "<MISSING>"
        street_address = j.split('"address_line_1":"')[1].split('"')[0].strip()
        phone = j.split('"main_phone":"')[1].split('"')[0].strip()
        state = j.split('"state":"')[1].split('"')[0].strip()
        postal = j.split('"postal_code":"')[1].split('"')[0].strip()
        country_code = "CA"
        city = j.split('"city":"')[1].split('"')[0].strip()
        store_number = "<MISSING>"
        latitude = j.split('"latitude":"')[1].split('"')[0].strip()
        longitude = j.split('"longitude":"')[1].split('"')[0].strip()
        hours_of_operation = (
            j.split('"hours":"')[1]
            .split(',"license"')[0]
            .replace("{", "")
            .replace("}", "")
            .replace('"', "")
            .replace(":", " ")
            .replace("from", "")
            .replace("to", "")
            .strip()
        )
        hours_of_operation = (
            hours_of_operation.replace("am,", "am -")
            .replace("  ", " ")
            .replace("pm,", "pm; ")
            .strip()
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
