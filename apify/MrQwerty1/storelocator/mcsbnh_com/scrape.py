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
    global_divs = tree.xpath("//li[@class='col-md-15 col-sm-4 col-12']")

    for gd in global_divs:
        city = "".join(gd.xpath(".//h2/text()")).strip()
        divs = gd.xpath(".//span[@class='d-block pl-3 pr-3']")

        for d in divs:
            location_name = "".join(d.xpath(".//p/strong/text()")).strip()

            street_address = (
                "".join(
                    d.xpath(".//p[@class='mb-0']/following-sibling::p/text()")
                ).strip()
                or "<MISSING>"
            )
            if "-" in street_address:
                street_address = street_address.split("-")[0].strip()

            state = "<MISSING>"
            postal = "<MISSING>"
            country_code = "US"
            store_number = "<MISSING>"
            phone = "<MISSING>"
            latitude = "<MISSING>"
            longitude = "<MISSING>"
            location_type = "<MISSING>"
            hours = d.xpath(".//div[contains(@id, '-lobby')]//text()")
            hours = list(filter(None, [h.strip() for h in hours]))
            hours_of_operation = ";".join(hours) or "<MISSING>"
            if "closed" in hours_of_operation:
                hours_of_operation = "Temporarily Closed"

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
