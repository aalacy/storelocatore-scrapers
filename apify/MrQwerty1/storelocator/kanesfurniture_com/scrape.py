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
    locator_domain = "https://www.kanesfurniture.com/"
    api_url = "https://www.kanesfurniture.com/pages/store-locations"

    session = SgRequests()
    r = session.get(api_url)
    tree = html.fromstring(r.text)
    divs = tree.xpath("//article[@class='location']")

    for d in divs:
        location_name = "".join(
            d.xpath(".//h4[@class='location__hdg']/a/text()")
        ).strip()
        slug = "".join(d.xpath(".//h4[@class='location__hdg']/a/@href"))
        page_url = f"https://www.kanesfurniture.com{slug}"
        line = d.xpath(".//address[@class='location__address']/p/text()")
        line = list(filter(None, [l.strip() for l in line]))

        street_address = line[0]
        line = line[1]
        city = line.split(",")[0].strip()
        line = line.split(",")[1].strip()
        state = line.split()[0]
        postal = line.split()[1]
        country_code = "US"
        store_number = "<MISSING>"
        phone = (
            "".join(d.xpath(".//a[@class='location__phone']/text()")).strip()
            or "<MISSING>"
        )
        latitude = "".join(d.xpath("./@data-lat")) or "<MISSING>"
        longitude = "".join(d.xpath("./@data-lng")) or "<MISSING>"
        location_type = "<MISSING>"

        _tmp = []
        keys = d.xpath(".//div[@class='location__hours']/p/b/text()")
        values = d.xpath(".//div[@class='location__hours']/p/text()")
        values = list(filter(None, [v.strip() for v in values]))

        for k, v in zip(keys, values):
            _tmp.append(f"{k.strip()} {v.strip()}")

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
