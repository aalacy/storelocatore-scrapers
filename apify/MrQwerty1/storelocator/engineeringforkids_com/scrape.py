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
    locator_domain = "https://www.engineeringforkids.com/"
    api_url = "https://www.engineeringforkids.com/locations/"

    session = SgRequests()
    r = session.get(api_url)
    tree = html.fromstring(r.text)
    divs = tree.xpath("//ul[@data-role='results']/li[@class='location']")

    for d in divs:
        line = d.xpath(".//address//text()")
        line = list(filter(None, [l.strip() for l in line]))

        street_address = (
            "".join(line[:-1]).replace("Engineering for Kids,", "").strip()
            or "<MISSING>"
        )
        line = line[-1]
        city = line.split(",")[0].strip() or "<MISSING>"
        line = line.split(",")[-1].strip()
        state = line.split()[0] or "<MISSING>"
        postal = " ".join(line.split()[1:]) or "<MISSING>"
        country = "".join(d.xpath("./@data-country"))
        if country == "usa":
            country_code = "US"
        else:
            country_code = "CA"
        store_number = "".join(d.xpath("./@data-loc-id")) or "<MISSING>"
        slug = "".join(d.xpath("./@data-href")) or "<MISSING>"
        page_url = f"https://www.engineeringforkids.com{slug}"
        location_name = "".join(d.xpath(".//div[@class='title']/h4/text()")).strip()
        phone = "".join(d.xpath(".//a[@class='phone']/text()")).strip() or "<MISSING>"
        latitude = "".join(d.xpath("./@data-latitude")) or "<MISSING>"
        longitude = "".join(d.xpath("./@data-longitude")) or "<MISSING>"
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
