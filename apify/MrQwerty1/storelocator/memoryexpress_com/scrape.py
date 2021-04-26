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
    locator_domain = "https://www.memoryexpress.com"
    api_url = "https://www.memoryexpress.com/Stores"

    session = SgRequests()
    r = session.get(api_url)
    tree = html.fromstring(r.text)
    divs = tree.xpath("//article[@class='c-shst-summary']")

    for d in divs:
        location_name = "".join(
            d.xpath(".//div[@class='c-shst-summary__header']//h3/text()")
        ).strip()
        slug = "".join(d.xpath(".//div[@class='c-shst-summary__header']/a/@href"))
        page_url = f"{locator_domain}{slug}"
        line = d.xpath(".//address[@class='c-shst-summary__address']/text()")
        line = list(filter(None, [l.strip() for l in line]))

        phone = line.pop().replace("Phone:", "").strip()
        street_address = line[0]
        if "(" in street_address:
            street_address = street_address.split("(")[0].strip()
        line = line[1]
        city = line.split(",")[0].strip()
        line = line.split(",")[1].strip()
        state = line.split()[0]
        postal = line.replace(state, "").strip()
        country_code = "CA"
        store_number = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        location_type = "<MISSING>"

        _tmp = []
        li = d.xpath(".//div[@class='c-shst-summary__hours']//li")
        for l in li:
            value = " ".join("".join(l.xpath(".//text()")).split())
            _tmp.append(value)

        hours_of_operation = ";".join(_tmp) or "<MISSING>"

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
