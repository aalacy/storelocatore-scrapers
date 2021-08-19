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
    locator_domain = "https://www.compass.com/"
    page_url = "https://www.compass.com/about/offices/"

    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)
    divs = tree.xpath("//div[@class='offices-office']")

    for d in divs:
        location_name = "".join(
            d.xpath("./h3[@class='offices-officeTitle']/text()")
        ).strip()
        line = d.xpath("./p[@class='offices-officeDetail']/text()")
        street_address = line[0]
        if len(line) == 3:
            phone = line[-1].replace("O:", "")
        else:
            phone = "<MISSING>"
        line = line[1]
        state = line.split()[-2]
        postal = line.split()[-1]
        if len(state) > 2:
            continue
        city = line.replace(state, "").replace(postal, "").strip()
        country_code = "US"

        store_number = "<MISSING>"
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

        t = tuple(row[2:6])
        if t not in s:
            s.add(t)
            out.append(row)

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
