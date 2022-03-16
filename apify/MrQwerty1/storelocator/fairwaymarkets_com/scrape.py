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
    locator_domain = "http://www.fairwaymarkets.com/"
    page_url = "http://www.fairwaymarkets.com/index.php/store-locations"

    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)
    divs = tree.xpath("//div[@class='art-Post']")

    for d in divs:
        location_name = "".join(
            d.xpath(".//span[@class='art-PostHeader']/text()")
        ).strip()
        line = d.xpath(".//div[@class='art-article']/p/text()")
        line = list(filter(None, [l.strip() for l in line]))
        street_address = line[0]
        city = line[1].split(",")[0].strip()
        state = line[1].split(",")[-1].replace(".", "").strip()
        postal = line[2]
        country_code = "CA"
        store_number = "<MISSING>"
        phone = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        location_type = "<MISSING>"
        hours_of_operation = line[3]

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
