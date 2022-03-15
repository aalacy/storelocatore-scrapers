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


def get_coords():
    coords = []
    session = SgRequests()
    r = session.get(
        "https://www.google.com/maps/d/u/0/kml?mid=1mg6lD4Gk5vqnFFFH0aTIdbBc9cvbKTvX&forcekml=1"
    )
    tree = html.fromstring(r.content)
    markers = tree.xpath("//coordinates/text()")
    for m in markers:
        m = m.replace(",0", "")
        lng, lat = m.split(",")
        coords.append((lat.strip(), lng.strip()))

    return coords


def fetch_data():
    out = []
    coords = get_coords()
    locator_domain = "http://rallystores.com/"
    page_url = "http://rallystores.com/locations/"

    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)
    divs = tree.xpath("//div[@class='page-content']/h3")

    for d in divs:
        location_name = "".join(d.xpath("./text()")).strip()
        street_address = "".join(d.xpath("./following-sibling::p[1]//text()")).strip()
        line = "".join(d.xpath("./following-sibling::p[2]//text()")).strip()
        city = line.split(",")[0].strip()
        line = line.split(",")[1].strip()
        state = line.split()[0]
        postal = line.split()[1]
        country_code = "US"
        store_number = location_name.split("#")[1].split()[0]
        phone = "".join(d.xpath("./following-sibling::p[3]//text()")).strip()
        latitude, longitude = coords.pop(0)
        location_type = "<MISSING>"
        hours_of_operation = "<MISSING>"

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
