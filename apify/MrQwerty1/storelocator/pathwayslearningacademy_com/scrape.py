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
    locator_domain = "https://www.pathwayslearningacademy.com/"
    api = "https://www.pathwayslearningacademy.com/locations/"

    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    r = session.get(api, headers=headers)
    tree = html.fromstring(r.text)
    divs = tree.xpath("//div[@class='locationCard']")

    for d in divs:
        page_url = api
        location_name = "".join(d.xpath(".//h2[@class='school']//text()")).strip()
        slug = "".join(d.xpath(".//a[@class='schoolNameLink']/@href"))
        if slug:
            page_url = f"https://www.pathwayslearningacademy.com{slug}"

        street_address = (
            "".join(
                d.xpath(".//div[@class='addrMapDetails']//span[@class='street']/text()")
            ).strip()
            or "<MISSING>"
        )
        line = (
            "".join(
                d.xpath(
                    ".//div[@class='addrMapDetails']//span[@class='cityState']/text()"
                )
            ).strip()
            or "<MISSING>, <MISSING> <MISSING>"
        )
        city = line.split(",")[0].strip()
        line = line.split(",")[1].strip()
        state = line.split()[0]
        postal = line.split()[1]
        country_code = "US"
        store_number = "".join(d.xpath("./@data-school-id")) or "<MISSING>"
        phone = "".join(d.xpath(".//span[@class='tel']/text()")).strip() or "<MISSING>"
        latitude = (
            "".join(
                d.xpath(
                    ".//div[@class='addrMapDetails']//span[@data-latitude]/@data-latitude"
                )
            )
            or "<MISSING>"
        )
        longitude = (
            "".join(
                d.xpath(
                    ".//div[@class='addrMapDetails']//span[@data-longitude]/@data-longitude"
                )
            )
            or "<MISSING>"
        )
        location_type = "<MISSING>"
        if d.xpath(".//div[@class='schoolFeature']"):
            location_type = "Coming Soon"
        hours_of_operation = (
            "".join(d.xpath(".//p[@class='hours']/text()")).strip() or "<MISSING>"
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
