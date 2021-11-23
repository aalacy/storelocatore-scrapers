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


def get_coords_from_google_url(url):
    try:
        latitude = url.split("&lat=")[1].split("&")[0]
        longitude = url.split("&lon=")[1].split("&")[0]
    except IndexError:
        latitude, longitude = "<MISSING>", "<MISSING>"

    return latitude, longitude


def fetch_data():
    out = []
    coords = []
    locator_domain = "https://tcbwa.com/"
    page_url = "https://tcbwa.com/Contact.html"

    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text.replace("<!--", "").replace("-->", ""))
    divs = tree.xpath("//h3/following-sibling::a")
    blocks = tree.xpath("//div[@id='overlay']/div")
    for b in blocks:
        text = "".join(b.xpath(".//a/@href"))
        lat, lng = get_coords_from_google_url(text)
        coords.append((lat, lng))

    for d in divs:
        location_name = "".join(d.xpath("./preceding-sibling::h3/text()")).strip()

        line = d.xpath(".//p/text()")
        line = list(filter(None, [l.strip() for l in line]))
        street_address = line[1]
        line = line[-1]
        city = line.split(",")[0].strip()
        line = line.split(",")[1].strip()
        state = line.split()[0]
        postal = line.split()[1]
        country_code = "US"
        store_number = "<MISSING>"
        phone = (
            "".join(
                tree.xpath(
                    "//td[text()='Bank by Phone']/following-sibling::td[1]/text()"
                )
            ).strip()
            or "<MISSING>"
        )
        latitude, longitude = coords.pop(0)
        location_type = "<MISSING>"
        hours_of_operation = "".join(
            tree.xpath(
                "//h2[text()='Hours of Operation']/following-sibling::p[1]/text()"
            )
        ).strip()

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
