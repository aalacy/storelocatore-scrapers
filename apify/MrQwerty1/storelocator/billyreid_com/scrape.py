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
        if url.find("ll=") != -1:
            latitude = url.split("ll=")[1].split(",")[0]
            longitude = url.split("ll=")[1].split(",")[1].split("&")[0]
        else:
            latitude = url.split("@")[1].split(",")[0]
            longitude = url.split("@")[1].split(",")[1]
    except IndexError:
        latitude, longitude = "<MISSING>", "<MISSING>"

    return latitude, longitude


def fetch_data():
    out = []
    locator_domain = "https://www.billyreid.com/"
    page_url = "https://www.billyreid.com/pages/our-stores"

    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)
    divs = tree.xpath("//div[@class='store']")

    for d in divs:
        location_name = "".join(d.xpath(".//h3[@class='store__title']/text()")).strip()
        if "coming soon" in location_name.lower():
            continue

        line = d.xpath(".//address//text()")
        line = list(filter(None, [l.strip() for l in line]))
        street_address = ", ".join(line[:-1])
        line = line[-1]
        city = line.split(",")[0].strip()
        line = line.split(",")[1].strip()
        state = line.split()[0].replace(".", "")
        postal = line.split()[-1]
        country_code = "US"

        store_number = "<MISSING>"
        phone = (
            "".join(d.xpath(".//a[@class='store__phone']/text()")).strip()
            or "<MISSING>"
        )
        text = "".join(d.xpath(".//address//a/@href"))
        latitude, longitude = get_coords_from_google_url(text)
        location_type = "<MISSING>"

        hours = "".join(d.xpath(".//div[@class='store__hours']/p/text()")).strip()
        if hours:
            hours = (
                hours.split("open")[1]
                .split(", and")[0]
                .replace("(", "")
                .replace(")", "")
                .strip()
            )

        hours_of_operation = hours or "<MISSING>"

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
