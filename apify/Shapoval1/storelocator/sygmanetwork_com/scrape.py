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

    locator_domain = "http://sygmanetwork.com"
    page_url = "http://sygmanetwork.com/Contact.html#locations"

    session = SgRequests()

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(page_url, headers=headers)

    tree = html.fromstring(r.text)
    jsblock = (
        "".join(
            tree.xpath('//script[contains(text(), "var sygmaLocations = ")]/text()')
        )
        .split("var sygmaLocations = ")[1]
        .split(";")[0]
    )
    js = json.loads(jsblock)
    for j in js:

        street_address = j.get("address")
        city = j.get("city")
        state = j.get("state")
        postal = j.get("zip")
        store_number = "<MISSING>"
        location_name = j.get("name")
        latitude = j.get("latLng")[0]
        longitude = j.get("latLng")[1]
        country_code = "US"
        location_type = "Sygma Network"
        phone = j.get("phone")[0].get("main")
        tmp = []
        try:
            hours = j.get("hours")[1].values()
        except:
            hours = "<MISSING>"
        if hours != "<MISSING>":
            for h in hours:
                for a in h:
                    times = a.get("time")
                    line = f"{times}"
                    tmp.append(line)

        hours_of_operation = (
            " ; ".join(tmp).replace("Business Office Hours ;", "").strip()
        ) or "<MISSING>"

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
