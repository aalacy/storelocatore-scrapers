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
    locator_domain = "https://www.davesmarkets.com/"
    page_url = "https://www.davesmarkets.com/locations.shtml"

    session = SgRequests()
    r = session.get(page_url)
    tree = html.fromstring(r.text)
    bb = tree.xpath("//td/b")

    for b in bb:
        location_name = "".join(b.xpath("./u/text()")).replace("-", "").strip()
        line = "".join(b.xpath("./u/a/@href"))
        if "mapquest" in line:
            street_address = line.split("address=")[1].split("&")[0].replace("+", " ")
            city = line.split("city=")[1].split("&")[0]
            state = line.split("state=")[1].split("&")[0]
            postal = line.split("zipcode=")[1].split("&")[0]
            latitude = line.split("latitude=")[1].split("&")[0]
            longitude = line.split("longitude=")[1].split("&")[0]
        else:
            adr = "".join(b.xpath("./following-sibling::text()")[:2]).strip()
            street_address = adr.split(",")[0].strip()
            city = adr.split(",")[1].strip()
            postal = adr.split(",")[-1].strip()
            state = "<MISSING>"
            latitude = "<MISSING>"
            longitude = "<MISSING>"

        country_code = "US"
        store_number = "<MISSING>"

        table = b.xpath("./following-sibling::table[1]")[0]
        phone = (
            "".join(
                table.xpath(".//td[text()='Phone']/following-sibling::td[1]/text()")
            ).strip()
            or "<MISSING>"
        )
        location_type = "<MISSING>"

        _tmp = []
        tr = table.xpath(".//tr[./td[text()='Hours:']]/following-sibling::tr")
        for t in tr:
            if len(t.xpath("./td")) < 3:
                break
            day = "".join(t.xpath("./td[2]/text()")).strip()
            time = "".join(t.xpath("./td[3]/text()")).strip()
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
