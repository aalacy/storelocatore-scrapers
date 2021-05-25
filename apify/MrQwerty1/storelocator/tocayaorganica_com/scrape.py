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
    locator_domain = "https://tocayaorganica.com/"
    page_url = "https://tocayaorganica.com/locations/"

    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)
    divs = tree.xpath("//div[contains(@class, 'locations__location location-')]")

    for d in divs:
        location_name = "".join(d.xpath("./h2/text()")).strip()
        additional = d.xpath(".//div[@class='locations__location-info']/text()")
        additional = list(filter(None, [a.strip() for a in additional]))
        line = d.xpath("./a[@class='locations__location-address']/text()")
        line = list(filter(None, [l.strip() for l in line]))

        street_address = line[0]
        line = line[-1]
        city = line.split(",")[0].strip()
        line = line.split(",")[-1].strip()
        state = line.split()[0]
        postal = line.replace(state, "").strip()
        country_code = "US"
        store_number = "<MISSING>"
        phone = additional.pop() or "<MISSING>"
        latitude = (
            "".join(d.xpath(".//span[@data-from-lat]/@data-from-lat")) or "<MISSING>"
        )
        longitude = (
            "".join(d.xpath(".//span[@data-from-lon]/@data-from-lon")) or "<MISSING>"
        )
        location_type = "<MISSING>"
        hours_of_operation = additional.pop() or "<MISSING>"
        if hours_of_operation.startswith(": "):
            hours_of_operation = hours_of_operation[2:]

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
