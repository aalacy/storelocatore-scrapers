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
    locator_domain = "https://mcsbnh.com/"
    page_url = "https://www.themerrimack.com/about/locations/"

    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)
    global_divs = tree.xpath("//h3/following-sibling::div[.//div[@class='grid-50']]")

    for gd in global_divs:
        city = "".join(gd.xpath("./preceding-sibling::h3[1]/a/text()")).strip()
        divs = gd.xpath(".//div[.//div[@class='grid-50']]")

        for d in divs:
            location_name = "".join(d.xpath(".//p/strong/text()")).strip()

            street_address = "".join(d.xpath(".//p/text()")).strip() or "<MISSING>"
            if "(" in street_address:
                street_address = street_address.split("(")[0].strip()
            if "-" in street_address:
                street_address = street_address.split("-")[0].strip()
            state = "<MISSING>"
            postal = "<MISSING>"
            country_code = "US"
            store_number = "<MISSING>"
            phone = (
                "".join(d.xpath(".//li[@class='phone first']/text()"))
                .replace("Phone:", "")
                .strip()
                or "<MISSING>"
            )
            if "·" in phone:
                phone = phone.split("·")[0].strip()
            latitude = "<MISSING>"
            longitude = "<MISSING>"
            location_type = "<MISSING>"
            hours = d.xpath(".//div[@class='grid-50 lobby']/p[last()]/text()")
            hours = list(filter(None, [h.strip() for h in hours]))
            hours_of_operation = ";".join(hours) or "<MISSING>"

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
