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


def get_nonce():
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    data = {"action": "locatornonce"}

    r = session.post(
        "https://truenorthstores.com/wp-admin/admin-ajax.php",
        headers=headers,
        data=data,
    )

    return r.json()["nonce"]


def fetch_data():
    out = []
    locator_domain = "https://truenorthstores.com/"
    api_url = "https://truenorthstores.com/wp-admin/admin-ajax.php"
    data = {
        "action": "locate",
        "locatorNonce": get_nonce(),
        "distance": "5000",
        "latitude": "42.2687314",
        "longitude": "-82.95822129999999",
        "unit": "miles",
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }

    session = SgRequests()
    r = session.post(api_url, data=data, headers=headers)
    js = r.json()["results"]

    for j in js:
        source = j.get("output")
        tree = html.fromstring(source)
        line = tree.xpath(".//div[@class='int_locations_left_info']/p/text()")
        line = list(filter(None, [l.strip() for l in line]))

        phone = "<MISSING>"
        if line[-1][0].isdigit() or line[-1][0] == "(":
            phone = line.pop()

        street_address = ", ".join(line[:-1])
        line = line[-1]
        city = line.split(",")[0].strip()
        line = line.split(",")[1].strip()
        state = line.split()[0]
        postal = line.split()[1]
        country_code = "US"
        store_number = j.get("id") or "<MISSING>"
        page_url = j.get("permalink") or "<MISSING>"
        location_name = j.get("title")
        latitude = j.get("latitude") or "<MISSING>"
        longitude = j.get("longitude") or "<MISSING>"
        location_type = "<MISSING>"
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
