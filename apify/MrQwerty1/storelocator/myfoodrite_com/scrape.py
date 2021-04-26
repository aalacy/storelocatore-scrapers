import csv
import yaml

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
    locator_domain = "https://www.myfoodrite.com/"
    page_url = "https://www.myfoodrite.com/locations/"

    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)
    divs = tree.xpath(
        "//div[@class='store-list-row-container store-bucket filter-rows']"
    )
    text = "".join(
        tree.xpath("//script[contains(text(), 'var storelatlngs =')]/text()")
    )
    text = text.split("var storelatlngs = ")[1].split(",];")[0] + "]"
    coords = yaml.load(text, Loader=yaml.Loader)
    cnt = 0

    for d in divs:
        location_name = "".join(d.xpath(".//a[@class='store-name']/text()")).strip()
        line = d.xpath(".//div[@class='store-address']/text()")
        line = list(filter(None, [l.strip() for l in line]))

        street_address = ", ".join(line[:-1])
        line = line[-1]
        city = line.split(",")[0].strip()
        line = line.split(",")[1].strip()
        postal = line.split()[-1]
        state = line.replace(postal, "").strip()
        country_code = "US"
        store_number = (
            "".join(d.xpath(".//div[@class='store-number']/text()")) or "<MISSING>"
        )
        phone = (
            "".join(d.xpath(".//a[@class='store-phone']/text()")).strip() or "<MISSING>"
        )
        loc = coords[cnt]
        latitude = loc.get("lat") or "<MISSING>"
        longitude = loc.get("lng") or "<MISSING>"
        location_type = "<MISSING>"

        _tmp = []
        text = d.xpath(".//div[@class='store-list-row-item-col02']/text()")
        for t in text:
            if t.strip() and "Manager" not in t:
                _tmp.append(t)

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
        cnt += 1

    return out


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
