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
    locator_domain = "http://countrywaffles.com/"
    page_url = "http://countrywaffles.com/_findus.php"
    api_url = "https://www.google.com/maps/d/u/0/kml?mid=1V6dTd81GPRozVEkURD4uvaG8MW1Yb91y&forcekml=1"

    session = SgRequests()
    r = session.get(api_url)
    tree = html.fromstring(r.content)
    divs = tree.xpath("//placemark")

    for d in divs:
        line = "".join(d.xpath("./name/text()")).strip()
        location_name = line.split("-")[0].strip()
        street_address = line.split("-")[-1].strip()
        city = "<INACCESSIBLE>"
        state = "<INACCESSIBLE>"
        postal = "<INACCESSIBLE>"
        country_code = "US"
        store_number = location_name.split("#")[-1]
        phone = "".join(d.xpath("./description/text()"))
        longitude, latitude = (
            "".join(d.xpath(".//coordinates/text()")).strip().split(",")[:2]
        )
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
