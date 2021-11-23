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
    locator_domain = "https://chippewavalleybank.com/"
    page_url = "https://chippewavalleybank.com/Locations-Hours-ATMs"

    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    divs = tree.xpath(
        "//h2[text()='Locations & Hours']/following-sibling::table[1][@class='Table-Grid']//tr"
    )

    for d in divs:
        location_name = "".join(d.xpath(".//h3/strong/text()")).strip()
        line = d.xpath(".//p[./img]/following-sibling::p[1]//text()")
        line = list(filter(None, [l.strip() for l in line]))
        street_address = ", ".join(line[:-1])
        line = line[-1]
        city = line.split(",")[0].strip()
        line = line.split(",")[1].strip()
        state = line.split()[0]
        postal = line.split()[1]
        country_code = "US"
        store_number = "<MISSING>"
        phone = (
            d.xpath(".//p[contains(text(), 'Toll')]/text()")[0].split("Toll")[0].strip()
            or "<MISSING>"
        )
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        location_type = "<MISSING>"
        hours_of_operation = "".join(
            d.xpath(
                ".//h4[contains(text(), 'Lobby Hours:')]/following-sibling::p[1]/text()"
            )
        )
        if not hours_of_operation:
            hours_of_operation = (
                " ".join(
                    d.xpath(
                        ".//h4[contains(text(), 'Drive-Up Hours')]/following-sibling::p/text()"
                    )
                )
                or "<MISSING>"
            )

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
