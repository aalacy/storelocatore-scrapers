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
    locator_domain = "https://www.chucksroadhouse.com"
    page_url = "https://www.chucksroadhouse.com/locations/"

    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[./a[@class="cta-button "]]')

    for d in div:
        line = d.xpath(".//p[2]/text()")
        street_address = "".join(line[0])
        postal = "<MISSING>"
        state = "<MISSING>"
        country_code = "CA"
        store_number = "<MISSING>"
        location_name = "".join(d.xpath(".//h2/text()"))
        city = location_name
        phone = "".join(line[1])
        location_type = "<MISSING>"
        hours_of_operation = "<MISSING>"
        if len(line) == 3:
            hours_of_operation = "".join(line[2])
        if phone.find("Location") != -1:
            hours_of_operation = "Coming Soon"
            phone = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
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
