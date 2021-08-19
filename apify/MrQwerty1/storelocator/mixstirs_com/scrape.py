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
    locator_domain = "https://mixstirs.com/"
    page_url = "https://mixstirs.com/locations.htm"

    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)
    keys = tree.xpath(
        "//td[@height='30']//table[.//div[contains(text(), 'Coming')]]/preceding-sibling::table//td[@class='main-blue']"
    )
    values = tree.xpath(
        "//td[@height='30']//table[.//div[contains(text(), 'Coming')]]/preceding-sibling::table//td[@class='main-red']"
    )

    for k, v in zip(keys, values):
        location_name = "".join(k.xpath("./text()")).strip()
        line = v.xpath("./text()")
        line = list(filter(None, [l.strip() for l in line]))

        phone = "<MISSING>"
        if line[-1][0].isdigit():
            phone = line.pop()

        street_address = line[-2]
        line = line[-1]
        city = line.split(",")[0].strip()
        line = line.split(",")[1].strip()
        state = line.split()[0]
        postal = line.split()[1]
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
        out.append(row)

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
