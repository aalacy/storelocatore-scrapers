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
    locator_domain = "https://www.trinaturk.com/"
    page_url = "https://www.trinaturk.com/pages/boutiques"

    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)
    divs = tree.xpath("//div[@class='row-center']")

    for d in divs:
        line = d.xpath(".//div[@class='wrapper-text-with-img']/p/text()")
        line = list(filter(None, [l.strip() for l in line]))
        location_name = line[0]

        street_address = ", ".join(line[1:-1])
        line = line[-1].replace(",", "")
        postal = line.split()[-1]
        state = line.split()[-2]
        city = line.split(state)[0].strip()
        country_code = "US"
        store_number = "<MISSING>"

        dt = d.xpath(".//div[@class='date-time']/p/text()")
        dt = list(filter(None, [d.strip() for d in dt]))

        phone = dt[-2]
        latitude, longitude = "<MISSING>", "<MISSING>"
        location_type = "<MISSING>"
        hours_of_operation = ";".join(dt[:-2]) or "<MISSING>"

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
