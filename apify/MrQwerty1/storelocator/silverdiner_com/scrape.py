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
    locator_domain = "https://www.silverdiner.com/"
    api_url = "https://www.silverdiner.com/locations"

    session = SgRequests()
    r = session.get(api_url)
    tree = html.fromstring(r.text)
    divs = tree.xpath(
        "//div[@class='panel-bootstrap panels-bootstrap-locations_teaser']"
    )

    for d in divs:
        street_address = "".join(d.xpath(".//span[@class='street']/text()")).strip()
        line = "".join(d.xpath(".//span[@class='city state zip']/text()")).strip()
        city = line.split(",")[0].strip()
        line = line.split(",")[1].strip()
        state = line.split()[0]
        postal = line.split()[1]
        country_code = "US"
        store_number = "<MISSING>"
        page_url = "https://www.silverdiner.com" + "".join(
            d.xpath(".//a[@class='btn bg-blue-l']/@href")
        )
        location_name = "".join(
            d.xpath(".//h3/a[contains(@href, 'location')]/text()")
        ).strip()
        if location_name.find("(") != -1:
            location_name = location_name.split("(")[0].strip()

        phone = "".join(d.xpath(".//div[@class='phone']/text()")).strip()
        try:
            latitude, longitude = "".join(
                d.xpath(".//div[@class='coordinates']/text()")
            ).split(",")
        except ValueError:
            latitude, longitude = "<MISSING>", "<MISSING>"
        location_type = "<MISSING>"

        _tmp = []
        sp = d.xpath(".//span[@class='oh-display']")
        for s in sp:
            day = "".join(s.xpath("./span[1]/text()")).strip()
            time = "".join(s.xpath("./span[2]/text()")).strip()
            _tmp.append(f"{day}: {time}")

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
