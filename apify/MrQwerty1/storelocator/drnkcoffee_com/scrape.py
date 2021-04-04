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
    s = set()
    locator_domain = "https://drnkcoffee.com/"
    page_url = "https://drnkcoffee.com/store-locations"

    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)
    divs = tree.xpath(
        "//div[@class='row clearfix location']//div[contains(@class,'grid4-12')]"
    )

    for d in divs:
        location_name = "".join(d.xpath(".//h4/text()")).strip()
        if location_name in s:
            continue

        s.add(location_name)
        line = "".join(d.xpath(".//address/text()")).strip().split(",")
        if "".join(line).find("Saudi") != -1:
            continue
        street_address = ", ".join(line[:-2]).strip()
        city = line[-2].strip()
        if not street_address:
            street_address = line[-2].split(".")[0].strip()
            city = line[-2].split(".")[1].strip()
        line = line[-1].strip()
        state = line.split()[0]
        postal = line.split()[1]
        if len(postal) < 5:
            postal = "<MISSING>"
        country_code = "US"
        store_number = "<MISSING>"
        phone = (
            "".join(d.xpath(".//a[@class='contact_call']/text()")).strip()
            or "<MISSING>"
        )
        latitude = "<MISSING>"
        longitude = "<MISSING>"
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
