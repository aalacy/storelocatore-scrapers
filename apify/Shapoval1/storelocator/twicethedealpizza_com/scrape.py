import csv
import json
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

    locator_domain = "http://twicethedealpizza.com/"
    api_url = "http://twicethedealpizza.com/locations.aspx"

    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//script[contains(text(), "var markers")]/text()')
    div = list(filter(None, [a.strip() for a in div]))
    div = (
        " ".join(div)
        .replace("\r\n", "")
        .replace("  ", " ")
        .replace("'", '"')
        .split("var markers = ")[1]
        .split(";")[0]
        .strip()
    )

    js = json.loads(div)

    for j in js:

        street_address = "".join(j.get("description")).replace(
            "Stratford", ",Stratford"
        )
        street_address = " ".join(street_address.split(",")[:-1]).strip()
        city = j.get("City") or "<MISSING>"
        state = "<MISSING>"
        postal = "<MISSING>"
        phone = j.get("Phone") or "<MISSING>"
        country_code = "CA"
        store_number = "<MISSING>"
        location_name = j.get("title") or "<MISSING>"
        latitude = j.get("lat") or "<MISSING>"
        longitude = j.get("lng") or "<MISSING>"
        location_type = "<MISSING>"
        page_url = "http://twicethedealpizza.com/locations.aspx"
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
