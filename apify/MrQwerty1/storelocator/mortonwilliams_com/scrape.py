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
    divs = reversed(tree.xpath("//div[@class='_2bafp']")[2:-2])
    cnt = 0

    for d in divs:
        lines = d.xpath(".//text()")
        lines = list(
            filter(
                None,
                [l.replace("\u200b", "").replace("\xa0", "").strip() for l in lines],
            )
        )

        if len(lines) == 1:
            c = lines[0]
            continue

        locations = [
            list(group)
            for k, group in groupby(lines, lambda x: "Manager" in x)
            if not k
        ]

        for loc in locations:
            street_address = loc.pop(0)
            location_name = street_address

            if loc[0].startswith("(") and loc[0].endswith(")"):
                location_name += f" {loc.pop(0)}"

            if "(" in street_address:
                street_address = street_address.split("(")[0].strip()
            if loc[0].startswith("New"):
                csz = loc.pop(0)
                city = csz.split(",")[0].strip()
                csz = csz.split(",")[1].strip()
                state = csz.split()[0]
                postal = csz.split()[-1]
            else:
                city = c
                state = "<MISSING>"
                postal = "<MISSING>"
                if city == "New Jersey":
                    city = "Jersey City"
                    state = c

                if city == "Bronx":
                    cnt += 1
                    if cnt > 1:
                        city = "Manhattan"

            phone = loc.pop(0)
            hours_of_operation = ";".join(loc)

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
