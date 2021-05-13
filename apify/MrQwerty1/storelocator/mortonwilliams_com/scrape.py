import csv

from itertools import groupby
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
    c = "<MISSING>"
    locator_domain = "https://www.mortonwilliams.com/"
    page_url = "https://www.mortonwilliams.com/our-locations"

    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    divs = reversed(tree.xpath("//div[@class='_1lRal']")[:-2])

    for d in divs:
        lines = d.xpath(".//text()")
        lines = list(filter(None, [l.replace("\u200b", "").strip() for l in lines]))
        if len(lines) == 1:
            c = lines[0]
            continue

        locations = [
            list(group)
            for k, group in groupby(lines, lambda x: "Manager" in x)
            if not k
        ]
        for loc in locations:
            hours_of_operation = loc.pop()
            phone = loc.pop()
            if loc[-1][0] == "(":
                loc.pop()

            street_address = loc.pop()
            location_name = street_address
            city = c
            state = "<MISSING>"
            postal = "<MISSING>"
            country_code = "US"
            store_number = "<MISSING>"
            latitude = "<MISSING>"
            longitude = "<MISSING>"
            location_type = "<MISSING>"

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
