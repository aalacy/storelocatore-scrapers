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
    coords = []
    locator_domain = "https://www.membersccu.org/"
    page_url = "https://www.membersccu.org/hours-and-locations"

    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    divs = tree.xpath("//div[@class='listbox']")
    text = "".join(
        tree.xpath("//script[contains(text(), 'var markers')]/text()")
    ).split("var marker, i")[1]
    for t in text.split("new google.maps.LatLng(")[1:]:
        lat, lng = t.split(");")[0].split(",")
        coords.append((lat.strip(), lng.strip()))

    for d in divs:
        location_name = "".join(d.xpath(".//span[@class='cuname']/a/text()")).strip()
        line = d.xpath(".//p[@class='locicons']/following-sibling::p[1]//text()")
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
            "".join(d.xpath(".//p[./strong[text()='Phone:']]/text()")).strip()
            or "<MISSING>"
        )
        latitude, longitude = coords.pop(0)
        location_type = "<MISSING>"

        hours = d.xpath(
            ".//p[./strong[contains(text(),'Lobby Hours')]]/following-sibling::*[1]/text()"
        )
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
