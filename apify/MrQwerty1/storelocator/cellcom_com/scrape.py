import csv
import re

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
    locator_domain = "https://www.cellcom.com/"
    page_url = "https://www.cellcom.com/location.html"

    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    cnt = 0
    text = "".join(tree.xpath("//script[contains(text(), 'LatLng')]/text()"))
    text = text.split("function setMarkers")[1].strip()
    coords = re.findall(r"LatLng(\(\d+.\d+, -?\d+.\d+\))", text)
    tr = tree.xpath("//table[@id='Locations']//tr[./td]")

    for t in tr:
        location_name = "".join(t.xpath("./td[1]/span[not(@style)]/text()")).strip()
        if not location_name:
            location_name = "".join(
                t.xpath("./td[1]/a[not(contains(@href, 'google'))]/text()")
            ).strip()
        line = t.xpath("./td[1]/a[contains(@href, 'google')]/text()")
        line = list(filter(None, [l.strip() for l in line]))
        street_address = line[0]
        line = line[-1]
        city = line.split(",")[0].strip()
        line = line.split(",")[-1].strip()
        state = line.split()[0]
        postal = line.split()[-1]
        country_code = "US"
        store_number = "<MISSING>"
        location_type = "".join(t.xpath("./td[1]/span[@style]/text()")).strip()

        try:
            phone = t.xpath("./td[2]/text()")[0].strip()
        except IndexError:
            phone = "<MISSING>"

        try:
            latitude, longitude = eval(coords[cnt])
        except IndexError:
            latitude = "<MISSING>"
            longitude = "<MISSING>"

        _tmp = []
        hours = t.xpath("./td[4]/text()")
        hours = list(filter(None, [h.strip() for h in hours]))
        for h in hours:
            if (
                h.lower().find("effective") != -1
                or h.lower().find("appointment") != -1
                or h.lower().find("available") != -1
            ):
                continue
            if (
                h.lower().find("open") != -1
                or h.lower().find("masks") != -1
                or h.lower().find("christmas") != -1
            ):
                continue
            _tmp.append(h)

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
