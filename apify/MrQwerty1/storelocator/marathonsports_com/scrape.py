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
    locator_domain = "https://www.marathonsports.com/"
    api = "https://www.marathonsports.com/locations/"

    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    r = session.get(api, headers=headers)
    tree = html.fromstring(r.text)
    divs = tree.xpath("//li[@data-workhours]")

    for d in divs:
        location_name = "".join(d.xpath("./@data-clubtitle")) or "<MISSING>"
        page_url = "".join(d.xpath("./@data-posturl")) or "<MISSING>"
        line = d.xpath(".//h2[@class='location-grid__title']//text()")
        line = list(filter(None, [l.strip() for l in line]))
        street_address = ", ".join(line[:-1])
        line = line[-1]
        city = line.split(",")[0].strip()
        line = line.split(",")[1].strip()
        state = line.split()[0]
        if state == "Wellesley":
            state = "<MISSING>"
        try:
            postal = line.split()[1]
        except IndexError:
            postal = "<MISSING>"
        country_code = "US"
        store_number = "<MISSING>"
        phone = (
            "".join(d.xpath(".//a[contains(@href, 'tel:')]/text()")).strip()
            or "<MISSING>"
        )
        latitude = "".join(d.xpath("./@data-marker-lat")) or "<MISSING>"
        longitude = "".join(d.xpath("./@data-marker-lng")) or "<MISSING>"
        color = "".join(d.xpath("./@data-color"))
        location_type = "<MISSING>"
        if color == "blue":
            location_type = "soundRunner"
        elif color == "red":
            location_type = "RUNNER'S ALLEY"
        elif color == "yellow":
            location_type = "Marathon Sports"
        hours_of_operation = (
            ";".join(eval("".join(d.xpath("./@data-workhours")).strip())) or "<MISSING>"
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
