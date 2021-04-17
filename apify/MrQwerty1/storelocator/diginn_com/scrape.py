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
    coords = dict()
    locator_domain = "https://www.diginn.com/"
    page_url = "https://www.diginn.com/locations"

    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)
    text = "".join(tree.xpath("//script[contains(text(), 'var locations = ')]/text()"))
    text = text.split("var locations = ")[1].split(";")[0]
    js = json.loads(text)

    for j in js:
        lat = j.get("latitude")
        lng = j.get("longitude")
        adr = j.get("street_address")
        key = adr.split()[0]
        coords[key] = (lat, lng)

    divs = tree.xpath("//div[contains(@class,'flex flex-col xs-2')]")
    for d in divs:
        location_name = "".join(d.xpath(".//div[@class='space-y-1']/div[1]/text()"))
        line = d.xpath(".//div[@class='space-y-1']/p/text()")
        line = list(filter(None, [l.strip() for l in line]))
        phone = line[-1]
        street_address = ", ".join(line[:-2])
        if "(" in street_address:
            street_address = street_address.split("(")[0].strip()
        line = line[-2].replace(",", "")
        postal = line.split()[-1]
        state = line.split()[-2]
        city = line.replace(postal, "").replace(state, "").strip()
        country_code = "US"
        store_number = "<MISSING>"

        key = street_address.split()[0]
        latitude, longitude = coords.get(key) or ("<MISSING>", "<MISSING>")
        location_type = "<MISSING>"

        hours_of_operation = (
            "".join(d.xpath(".//div[@class='space-y-1']/div[./p]//text()")).replace(
                "â", "-"
            )
            or "<MISSING>"
        )
        if "(" in hours_of_operation:
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
